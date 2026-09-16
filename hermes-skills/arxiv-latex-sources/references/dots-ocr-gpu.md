# dots.ocr GPU pipeline (VLM document OCR: math + tables + figures)

Validated 2026-08 on an HPC cluster (A100 via srun --overlap join of a
persistent allocation; 28 PDF pages, zero failures, ~70-95 s/page with the
eager-attention fallback). Use when a paper's math/tables must be extracted
with high fidelity AND figures are needed as images (pypdf text has NO math;
raw .tex has no figure content; dots.ocr gives LaTeX math + HTML tables +
embedded figure images).

## What it is
dots.ocr (rednote-hilab/dots.ocr): 1.7B vision-language model, prompt-driven
layout parsing. The `prompt_layout_all_en` prompt (in
`dots_ocr/utils/prompts.py`) produces a JSON layout: Formula -> LaTeX,
Table -> HTML, other text -> Markdown, elements in reading order. Input is
PAGE IMAGES (not PDFs) — render with PyMuPDF at 200 DPI first.

## Setup (per machine)
```bash
git clone https://github.com/rednote-hilab/dots.ocr.git dots-ocr
uv venv ~/.venvs/dots-ocr --python 3.11
uv pip install --python ~/.venvs/dots-ocr/bin/python torch --index-url https://download.pytorch.org/whl/cu128
uv pip install --python ~/.venvs/dots-ocr/bin/python -e dots-ocr \
  "transformers==4.56.1" qwen_vl_utils accelerate huggingface_hub PyMuPDF torchvision
  # torchvision is REQUIRED by qwen_vl_utils (easy to miss)
# weights (~5.7 GB, two safetensors shards):
uv run --with huggingface_hub python -c \
  "from huggingface_hub import snapshot_download; snapshot_download('rednote-hilab/dots.ocr', local_dir='dots-ocr/weights/DotsOCR')"
```
Cluster GPU driver is CUDA 12.8 -> torch cu128 wheels (default cu130 fails).

## Two transformers 4.56.1 pitfalls (both are hard blockers)

1. `AutoProcessor.from_pretrained` FAILS: "Received a NoneType for argument
   video_processor, but a BaseVideoProcessor was expected." The dots remote
   code (`configuration_dots.py`, `DotsVLProcessor.__init__`) never passes a
   video_processor; 4.56's ProcessorMixin rejects None. FIX: do NOT patch the
   HF cache file (`~/.cache/huggingface/modules/transformers_modules/...`) —
   HF re-syncs remote code and reverts it. Instead, at import time in your
   runner, load the class via
   `transformers.dynamic_module_utils.get_class_from_dynamic_module(
   "configuration_dots.DotsVLProcessor", weights_dir, trust_remote_code=True)`
   and monkeypatch `__init__` to build a real video processor
   (`transformers.video_processing_utils.BaseVideoProcessor()` — constructible
   bare) and forward it as `video_processor=` kwarg into
   `Qwen2_5_VLProcessor.__init__`, replicating the class body
   (image_token/image_token_id lines).

2. `apply_chat_template` FAILS with list content: "can only concatenate str
   (not 'list') to str". The TOKENIZER's chat_template is the generic Qwen2.5
   string-only template; the dots-specific template (image/video handling)
   lives in the model dir's `chat_template.json`. FIX: after building the
   processor, `processor.chat_template = json.load(open(weights_dir +
   '/chat_template.json'))['chat_template']`.

## Runner shape
- Load model with `attn_implementation="sdpa"` (fallback "eager"); flash-attn
  not required. The vision encoder prints "flash attention not available!
  fallback to eager" — that's the ~70-95 s/page cost driver.
- Per page: PIL image -> messages `[{"role":"user","content":[{"type":"image",
  "image": img}, {"type":"text","text": PROMPT}]}]` -> `apply_chat_template`
  (dots template) -> `processor(text=[text], images=[img], return_tensors="pt")`
  -> `model.generate(max_new_tokens=8192, do_sample=False)` -> decode.
- Parse the JSON layout tolerantly (regex for first `[...]` block), convert
  with `dots_ocr.utils.format_transformer.layoutjson2md(image, cells)`.
- Progress log per page with timestamps (mandatory for HPC jobs); dump raw
  responses to a `_debug/` dir on parse failure.
- Output .md files are large (base64 figures) — 2-4 MB per paper; fine as a
  vision-channel artifact, wasteful as text input (~650k tokens/paper).
