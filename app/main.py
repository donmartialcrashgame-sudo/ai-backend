import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Game API AI")
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.gguf")
MODEL_N_CTX = int(os.getenv("MODEL_N_CTX", "4096"))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "512"))

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are Game API AI, the official assistant for game-api.online. "
    "Be helpful, accurate, concise, and never invent API details. "
    "If information is not available in your knowledge, say so clearly."
)

app = FastAPI(title=APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://game-api.online",
        "https://www.game-api.online",
    ],
    allow_credentials=True,
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
            detail=(
                "AI model is not installed yet. Set MODEL_PATH to a local "
                "GGUF model file before using /api/chat."
            ),
        )

    try:
        from llama_cpp import Llama

        _llm = Llama(
            model_path=str(model_file),
            n_ctx=MODEL_N_CTX,
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


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "status": "online",
        "message": "Game API AI backend is running.",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_configured": Path(MODEL_PATH).exists(),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    llm = get_model()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(
        {"role": item.role, "content": item.content}
        for item in request.history[-20:]
    )
    messages.append({"role": "user", "content": request.message})

    try:
        result = llm.create_chat_completion(
            messages=messages,
            max_tokens=MODEL_MAX_TOKENS,
            temperature=0.3,
        )
        reply = result["choices"][0]["message"]["content"].strip()
        return ChatResponse(reply=reply, model=Path(MODEL_PATH).name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {exc}")
