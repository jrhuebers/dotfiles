---
name: paper-fetching
description: Fetch arXiv papers with their LaTeX sources and produce a traceable, LLM-readable corpus.
author: huebers
platforms: [linux, macos]
---

# Paper Fetching

Use when collecting papers for a research corpus. Prefer source-backed extraction over PDF-only text extraction.

## arXiv workflow

1. Verify each ID, title, and author list against the arXiv API; do not trust IDs from memory.
2. Download the latest PDF and source using the bare ID:
   `curl -sL https://arxiv.org/pdf/<id> -o arxiv_<id>.pdf`
   and `curl -sL -A "research-assistant/0.1" https://arxiv.org/e-print/<id> -o src/<id>.tar.gz`.
3. Record the concrete version from `https://export.arxiv.org/api/query?id_list=<id>`; rate-limit arXiv requests to about one per three seconds.
4. Safely extract the source, find the `.tex` file containing `\documentclass`, and run from its directory:
   `latexpand --empty-comments main.tex > arxiv_<id>.tex`.
5. Apply a verbatim-aware comment stripper that preserves escaped `\%` and `verbatim`, `lstlisting`, `minted`, and similar environments. Add a provenance header with ID, version, tool, main file, and fetch date.

Keep the original source tarball as canonical; the flattened `.tex` is derived. Run `figindex.py` afterward to make captions searchable. Use PDF text extraction only for quick searches, not as the primary reading format.

## Layout and policy

```text
papers/
  arxiv_<id>.pdf
  arxiv_<id>.tex
  src/<id>.tar.gz
```

Stage downloads before copying them into project `papers/` directories, which are normally gitignored. For non-arXiv papers, retain the PDF only and verify that the downloaded file is actually a PDF.

## Pitfalls

- Do not guess `main.tex`; filenames vary and small stubs may delegate to the real document.
- Run `latexpand` from the source directory so relative `\input` and `\include` paths resolve.
- Keep PDFs as visual ground truth and tarballs for reproducibility.
- Use a Slurm GPU allocation only for optional image OCR; downloading and flattening are ordinary CPU work.
