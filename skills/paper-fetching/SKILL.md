---
name: paper-fetching
description: Fetch arXiv papers into self-contained per-paper directories with searchable figures and references. Use when collecting papers for research.
---

# Paper fetching

With Python 3 and `latexpand` installed, run from this skill's directory:

```bash
python3 scripts/fetch_papers.py /path/to/papers 1706.03762 1810.04805
```

Use bare arXiv IDs. The command fetches the latest PDF and original source, flattens and cleans the LaTeX, materializes image and bibliography assets, verifies the corpus, and builds per-paper `FIGURES.md` and `REFERENCES.md` lookup files. It never overwrites an existing paper directory.

Each paper is self-contained:

```text
papers/<arxiv-id>/
  <arxiv-id>.pdf
  <arxiv-id>.tex
  <arxiv-id>.tar.gz
  FIGURES.md
  REFERENCES.md
  figures/       # extracted image assets
  bibliography/  # extracted .bib/.bbl/.bst/.bcf assets
```

If source is unavailable, the directory contains the PDF and `source-unavailable.txt` instead. A fetch or QA failure exits nonzero and leaves successful directories for inspection without rebuilding indexes. For existing papers only, run `scripts/qa_corpus.py`, `scripts/figindex.py`, or `scripts/refindex.py` separately.
