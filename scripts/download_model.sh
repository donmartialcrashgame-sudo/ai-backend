#!/bin/sh
set -eu

MODEL_PATH="${MODEL_PATH:-/tmp/model.gguf}"
MODEL_DIR="$(dirname "$MODEL_PATH")"
MODEL_URL="${MODEL_URL:-https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/1208e45d782fe18602c5eaf10e5758d5b0f24c03/Qwen3-0.6B-Q4_K_M.gguf?download=true}"

mkdir -p "$MODEL_DIR"

if [ -s "$MODEL_PATH" ]; then
  echo "AI model already exists at $MODEL_PATH; skipping download."
  exit 0
fi

echo "Downloading small Qwen3-0.6B Q4_K_M model with Hugging Face Hub..."
echo "Destination: $MODEL_PATH"

python - "$MODEL_PATH" "$MODEL_URL" <<'PY'
import sys
from pathlib import Path
from urllib.parse import urlparse
from huggingface_hub import hf_hub_download

output = Path(sys.argv[1])
url = sys.argv[2]
parsed = urlparse(url)
parts = parsed.path.strip("/").split("/")

try:
    repo_id = parts[0] + "/" + parts[1]
    resolve_index = parts.index("resolve")
    revision = parts[resolve_index + 1]
    filename = "/".join(parts[resolve_index + 2:])
except (ValueError, IndexError) as exc:
    raise RuntimeError("Unable to parse Hugging Face model URL") from exc

if not filename:
    raise RuntimeError("Model filename is missing from MODEL_URL")

downloaded = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    revision=revision,
    local_dir=str(output.parent),
    force_download=False,
)

downloaded_path = Path(downloaded)
if downloaded_path.resolve() != output.resolve():
    if output.exists():
        output.unlink()
    downloaded_path.replace(output)

size = output.stat().st_size
if size < 250 * 1024 * 1024:
    raise RuntimeError(f"Downloaded model is unexpectedly small: {size} bytes")

print(f"AI model download complete: {output}")
print(f"Model size: {size / (1024**2):.0f} MiB")
PY

ls -lh "$MODEL_PATH"
