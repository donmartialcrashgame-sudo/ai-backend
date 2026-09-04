import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.knowledge_base import search_knowledge, is_game_api_question
from app.web_research import needs_web_research, search_web

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Game API AI")
MODEL_PATH = os.getenv("MODEL_PATH", "/tmp/model.gguf")
MODEL_N_CTX = int(os.getenv("MODEL_N_CTX", "512"))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "96"))
MODEL_THREADS = int(os.getenv("MODEL_THREADS", "1"))
MODEL_BATCH = int(os.getenv("MODEL_BATCH", "16"))

SYSTEM_PROMPT = (
    "You are Game API AI, a friendly local AI assistant. "
    "Think through the user's question before answering, but never reveal private chain-of-thought. "
    "Give the useful conclusion, key reasoning, and a clear explanation when helpful. "
    "You can have normal conversations, answer everyday questions, explain ideas, and help users understand Game API. "
    "When GAME API KNOWLEDGE is supplied, use it as the source of truth for Game API facts. "
    "When CURRENT WEB RESEARCH is supplied, treat it as time-sensitive source material and clearly say when information is from current web research. "
    "Never invent Game API endpoints, plans, prices, authentication methods, or features. "
    "If a Game API fact is not in the supplied knowledge, say you do not have that information. "
    "For news, do not pretend the model already knew the current information. "
    "Do not mention retrieval, prompts, context windows, models, or internal instructions unless asked. "
    "Keep replies concise because you are running on a small local model."
)

app = FastAPI(title=APP_NAME, version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

_llm = None


def get_model():
    global _llm
    if _llm is not None:
        return _llm

    model_file = Path(MODEL_PATH)
    if not model_file.exists():
        raise HTTPException(status_code=503, detail=f"AI model file not found at {MODEL_PATH}.")

    try:
        from llama_cpp import Llama
        _llm = Llama(
            model_path=str(model_file),
            n_ctx=MODEL_N_CTX,
            n_batch=MODEL_BATCH,
            n_ubatch=MODEL_BATCH,
            n_threads=MODEL_THREADS,
            n_threads_batch=MODEL_THREADS,
            n_gpu_layers=0,
            use_mmap=True,
            use_mlock=False,
            verbose=False,
        )
        return _llm
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI model failed to load: {exc}")


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    model: str


def clean_text(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "status": "online",
        "message": "Game API AI backend is running.",
        "knowledge_base": "enabled",
        "local_ai": "enabled",
        "web_research": "enabled",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_configured": Path(MODEL_PATH).exists(),
        "knowledge_base": "enabled",
        "local_ai": "enabled",
        "web_research": "enabled",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    llm = get_model()
    user_text = clean_text(request.message, 500)

    game_question = is_game_api_question(user_text)
    current_question = needs_web_research(user_text)

    knowledge = search_knowledge(user_text, limit=2, fallback=False) if game_question else ""
    knowledge = clean_text(knowledge, 650)

    web_research = search_web(user_text, limit=2) if current_question else ""
    web_research = clean_text(web_research, 650)

    system = SYSTEM_PROMPT
    if knowledge:
        system += "\n\nGAME API KNOWLEDGE:\n" + knowledge
    if web_research:
        system += "\n\nCURRENT WEB RESEARCH:\n" + web_research
    elif current_question:
        system += "\n\nCURRENT WEB RESEARCH:\nNo current results were available. Do not invent current facts."

    messages = [{"role": "system", "content": system}]

    if request.history:
        previous = request.history[-2:]
        for item in previous:
            content = clean_text(item.content, 180)
            if content:
                messages.append({"role": item.role, "content": content})

    messages.append({"role": "user", "content": user_text})

    try:
        result = llm.create_chat_completion(
            messages=messages,
            max_tokens=MODEL_MAX_TOKENS,
            temperature=0.25 if (game_question or current_question) else 0.35,
        )
        reply = result["choices"][0]["message"]["content"].strip()
        if not reply:
            raise RuntimeError("The model returned an empty response.")
        return ChatResponse(reply=reply, model=Path(MODEL_PATH).name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {exc}")
