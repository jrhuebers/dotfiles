---
name: paper-fetching
description: Fetch current arXiv PDFs and original LaTeX, flatten source for reading, and verify a paper corpus.
author: huebers
platforms: [linux, macos]
---

# Paper Fetching

Use for source-backed paper collections. From this skill's directory, with Python 3 and `latexpand` (TeX Live or CTAN) installed:

```bash
python3 scripts/fetch_papers.py /path/to/papers 1706.03762 1810.04805
python3 scripts/qa_corpus.py /path/to/papers
python3 scripts/figindex.py /path/to/papers
```

The fetcher accepts bare modern arXiv IDs, checks titles/authors/version against the arXiv API, downloads the latest PDF and original source (polite ~3-second request spacing), safely extracts it in temporary staging, finds the largest real `\documentclass` main file, then runs `latexpand --keep-comments` from its directory (the historical `--empty-comments` destroys literal `%` inside verbatim). `flatten_tex.py` strips comments while preserving escaped `\%` and verbatim environments, and stamps provenance. Fetch refuses to overwrite existing papers; use a new directory to refresh and compare versions. When arXiv returns 404, PDF, or PS instead of LaTeX source, it keeps the PDF with an explicit `arxiv_<id>.source-unavailable.txt` marker; other download/processing failures fail rather than silently fabricating `.tex`.

Each paper yields `arxiv_<id>.pdf`, `arxiv_<id>.tex`, and `src/<id>.tar.gz` (or `.tex.gz`/`.tex` for single-file originals). Original source is canonical; flattened TeX is the primary LLM reading copy, PDF is visual ground truth. The figure index makes captions searchable but is not image OCR. Stage before copying into a project's normally gitignored `papers/`; verify the title of each PDF against API metadata before citing. Do not infer authors or IDs from memory.

## Where to run

A one- or few-paper fetch, flatten, QA, and caption-index run is light network I/O and modest CPU work. Run it directly in the current shell; if already inside a Slurm allocation (including mission-control), use that allocation and do not submit a nested `sbatch`/`srun` job just for these steps.

Do not run intensive CPU, memory, or GPU processing on a shared login node. For bulk corpus processing or image OCR/VLM, submit the intensive work to Slurm with appropriate resources; GPU OCR requires a GPU allocation.
