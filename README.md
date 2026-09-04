# Game API AI Backend

Self-hosted AI backend for `game-api.online`.

## Architecture

- FastAPI provides the HTTP API.
- `llama-cpp-python` runs a local GGUF language model.
- No OpenAI, Gemini, Anthropic, or other hosted AI API key is required.
- The model file is intentionally excluded from Git with `.gitignore`.

## Endpoints

- `GET /` — service information
- `GET /health` — health/model status
- `POST /api/chat` — chat with the local model

## Local setup

1. Create a Python virtual environment.
2. Install `requirements.txt`.
3. Put a compatible GGUF model at `models/model.gguf`, or set `MODEL_PATH`.
4. Start the server with:

```bash
uvicorn app.main:app --reload
```

The next stage is to select the model, add a knowledge system for the Game API documentation, and then connect the website AI gadget.
