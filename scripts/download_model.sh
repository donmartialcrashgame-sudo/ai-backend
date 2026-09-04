#!/bin/sh
set -eu

MODEL_PATH="${MODEL_PATH:-/var/data/model.gguf}"
MODEL_URL="${MODEL_URL:-https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf?download=true}"

mkdir -p "$(dirname "$MODEL_PATH")"

if [ -s "$MODEL_PATH" ]; then
  echo "AI model already exists at $MODEL_PATH; skipping download."
  exit 0
fi

tmp_path="${MODEL_PATH}.part"
echo "Downloading Qwen3-4B Q4_K_M model..."
echo "Destination: $MODEL_PATH"

# Resume an interrupted download when possible. The model is about 2.5 GB.
curl -L --fail --retry 5 --retry-delay 5 -C - "$MODEL_URL" -o "$tmp_path"
mv "$tmp_path" "$MODEL_PATH"

echo "AI model download complete."
ls -lh "$MODEL_PATH"
