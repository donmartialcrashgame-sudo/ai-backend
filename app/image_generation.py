import base64
import json
import os
from urllib.request import Request, urlopen

IMAGE_ENGINE_URL = os.getenv("IMAGE_ENGINE_URL", "").rstrip("/")
IMAGE_ENGINE_API_KEY = os.getenv("IMAGE_ENGINE_API_KEY", "")


def is_image_request(query: str) -> bool:
    q = query.lower().strip()
    phrases = (
        "generate an image", "generate image", "create an image", "create image",
        "make an image", "make image", "draw an image", "draw me", "show me an image",
        "design an image", "design image", "picture of", "photo of", "illustration of",
        "generate a picture", "create a picture", "make a picture",
    )
    return any(p in q for p in phrases)


def generate_image(prompt: str) -> dict:
    """Call the self-hosted Game API image engine."""
    if not IMAGE_ENGINE_URL:
        raise RuntimeError(
            "The local image engine is not connected yet. Configure IMAGE_ENGINE_URL "
            "to the self-hosted image-generation service."
        )

    payload = json.dumps({
        "prompt": prompt,
        "steps": 12,
        "width": 512,
        "height": 512,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Game-API-AI/1.0",
    }
    if IMAGE_ENGINE_API_KEY:
        headers["x-api-key"] = IMAGE_ENGINE_API_KEY
        headers["Authorization"] = f"Bearer {IMAGE_ENGINE_API_KEY}"

    request = Request(
        f"{IMAGE_ENGINE_URL}/sdapi/v1/txt2img",
        data=payload,
        headers=headers,
        method="POST",
    )

    with urlopen(request, timeout=240) as response:
        result = json.loads(response.read().decode("utf-8"))

    images = result.get("images") or []
    if not images:
        raise RuntimeError("The image engine returned no image.")

    image_b64 = images[0]
    if image_b64.startswith("data:image"):
        data_url = image_b64
    else:
        data_url = "data:image/png;base64," + image_b64

    return {"image": data_url}
