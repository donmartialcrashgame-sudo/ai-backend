#!/bin/sh
set -eu

MODEL_PATH="${MODEL_PATH:-/var/data/model.gguf}"
MODEL_DIR="$(dirname "$MODEL_PATH")"
MODEL_URL="${MODEL_URL:-https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf?download=true}"

mkdir -p "$MODEL_DIR"

if [ -s "$MODEL_PATH" ]; then
  echo "AI model already exists at $MODEL_PATH; skipping download."
  exit 0
fi

echo "Downloading Qwen3-4B Q4_K_M model with Hugging Face Hub..."
echo "Destination: $MODEL_PATH"

python - "$MODEL_PATH" "$MODEL_URL" <<'PY'
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

output = Path(sys.argv[1])
url = sys.argv[2]

# The environment variable remains supported for custom model URLs, but the
# default Qwen URL is downloaded through huggingface_hub so Xet-backed files
# are handled correctly instead of treating a small redirect/error response
# as the model.
if url.startswith("https://huggingface.co/"):
    parts = url.split("/Qwen/", 1)
    if len(parts) != 2:
        raise RuntimeError("Unable to parse Hugging Face model URL")
    repo_and_file = parts[1].split("/resolve/main/", 1)
    if len(repo_and_file) != 2:
        raise RuntimeError("Unable to parse Hugging Face model URL")
    repo_id = "Qwen/" + repo_and_file[0]
    filename = repo_and_file[1].split("?", 1)[0]
    downloaded = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=str(output.parent),
        force_download=False,
    )
    downloaded_path = Path(downloaded)
else:
    raise RuntimeError("MODEL_URL must be a Hugging Face model URL")

if downloaded_path.resolve() != output.resolve():
    downloaded_path.replace(output)

size = output.stat().st_size
if size < 100 * 1024 * 1024:
    raise RuntimeError(f"Downloaded model is unexpectedly small: {size} bytes")

print(f"AI model download complete: {output}")
print(f"Model size: {size / (1024**3):.2f} GiB")
PY

ls -lh "$MODEL_PATH"
