import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.site_knowledge import search_site

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Game API AI")
MODEL_PATH = os.getenv("MODEL_PATH", "/tmp/model.gguf")
MODEL_N_CTX = int(os.getenv("MODEL_N_CTX", "512"))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "128"))
MODEL_THREADS = int(os.getenv("MODEL_THREADS", "1"))
MODEL_BATCH = int(os.getenv("MODEL_BATCH", "16"))

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are Game API AI, the official assistant for game-api.online. "
    "Be helpful, accurate, concise, and never invent API details. "
    "Use the live Game API website context supplied with each request when it is relevant. "
    "Treat that context as the source of truth for Game API website information. "
    "If the website context does not contain the answer, say that clearly instead of guessing.",
)

app = FastAPI(title=APP_NAME, version="0.2.1")

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
        raise HTTPException(
            status_code=503,
            detail=f"AI model file not found at {MODEL_PATH}.",
        )

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
    except HTTPException:
        raise
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


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "status": "online",
        "message": "Game API AI backend is running.",
        "knowledge": "live game-api.online website search enabled",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_configured": Path(MODEL_PATH).exists(),
        "website_knowledge": "enabled",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    llm = get_model()

    # Keep the tiny 135M model inside its 512-token context window.
    # Website retrieval is useful, but sending too much retrieved text plus
    # conversation history can make llama.cpp reject the prompt.
    try:
        website_context = search_site(request.message)
    except Exception:
        website_context = "Website search is temporarily unavailable."

    website_context = website_context[:1400]
    knowledge_message = (
        "Game API website knowledge:\n" + website_context
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": knowledge_message})

    # Only keep a small amount of recent conversation so the prompt remains
    # safe for the small local model.
    recent_history = request.history[-2:]
    for item in recent_history:
        content = item.content[:700]
        messages.append({"role": item.role, "content": content})

    messages.append({"role": "user", "content": request.message[:1500]})

    try:
        result = llm.create_chat_completion(
            messages=messages,
            max_tokens=MODEL_MAX_TOKENS,
            temperature=0.3,
        )
        reply = result["choices"][0]["message"]["content"].strip()
        if not reply:
            raise RuntimeError("The model returned an empty response.")
        return ChatResponse(reply=reply, model=Path(MODEL_PATH).name)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {exc}")
