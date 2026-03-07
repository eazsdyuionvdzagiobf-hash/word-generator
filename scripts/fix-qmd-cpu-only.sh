#!/usr/bin/env bash
set -euo pipefail

QMD_LLM_JS="/usr/local/lib/node_modules/@tobilu/qmd/dist/llm.js"

if [[ ! -f "$QMD_LLM_JS" ]]; then
  echo "QMD llm.js not found: $QMD_LLM_JS" >&2
  exit 1
fi

python3 - <<'PY'
from pathlib import Path

p = Path('/usr/local/lib/node_modules/@tobilu/qmd/dist/llm.js')
text = p.read_text()

old = """            const gpuTypes = await getLlamaGpuTypes();
            // Prefer CUDA > Metal > Vulkan > CPU
            const preferred = [\"cuda\", \"metal\", \"vulkan\"].find(g => gpuTypes.includes(g));
            let llama;
            if (preferred) {
                try {
                    llama = await getLlama({ gpu: preferred, logLevel: LlamaLogLevel.error });
                }
                catch {
                    llama = await getLlama({ gpu: false, logLevel: LlamaLogLevel.error });
                    process.stderr.write(`QMD Warning: ${preferred} reported available but failed to initialize. Falling back to CPU.\\n`);
                }
            }
            else {
                llama = await getLlama({ gpu: false, logLevel: LlamaLogLevel.error });
            }"""

new = """            let llama;
            llama = await getLlama({ gpu: false, logLevel: LlamaLogLevel.error });"""

already = new in text and 'getLlama({ gpu: preferred, logLevel: LlamaLogLevel.error })' not in text
if already:
    print(f'Already patched: {p}')
else:
    if old not in text:
        raise SystemExit('Target block not found; patch manually.')
    p.write_text(text.replace(old, new))
    print(f'Patched: {p}')
PY

export NODE_LLAMA_CPP_GPU=false
export GGML_CUDA=OFF
export GGML_METAL=OFF
export GGML_VULKAN=OFF

cd /Users/huangjunjie/.openclaw/workspace
exec qmd embed -f
