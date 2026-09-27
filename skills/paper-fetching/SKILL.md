---
name: paper-fetching
description: Fetch arXiv papers into self-contained per-paper directories with searchable figures, references, and a corpus index. Use when collecting papers for research.
---

# Paper fetching

With Python 3 and `latexpand` installed, run from this skill's directory:

```bash
python3 scripts/fetch_papers.py /path/to/papers 1706.03762 1810.04805
```

Use bare arXiv IDs. The command fetches the latest PDF and original source, flattens and cleans the LaTeX, materializes image and bibliography assets, verifies the corpus, and builds `INDEX.md` plus per-paper `FIGURES.md` and `REFERENCES.md` lookup files. It never overwrites an existing paper directory.

Each corpus has this structure:

```text
papers/
  INDEX.md                 # all papers: IDs, versions, titles, authors, abstracts
  <arxiv-id>/
    metadata.json          # API metadata used to regenerate INDEX.md
    <arxiv-id>.pdf
    <arxiv-id>.tex
    <arxiv-id>.tar.gz      # canonical original source archive
    FIGURES.md             # captions and direct materialized image paths
    REFERENCES.md          # citation keys and bibliography entries
    figures/               # extracted image assets
    bibliography/          # extracted .bib/.bbl/.bst/.bcf assets
```

Treat `papers/` as generated, read-only corpus data. Do not manually edit, delete, rename, or overwrite any PDF, TeX, archive, metadata, index, figure, or bibliography file there. To change a corpus, fetch into a new directory or use the bundled index/QA scripts to regenerate derived files.

If source is unavailable, the paper directory contains the PDF, metadata, and `source-unavailable.txt` instead. A fetch or QA failure exits nonzero and leaves successful directories for inspection without rebuilding indexes. For existing papers only, run `scripts/qa_corpus.py`, `scripts/figindex.py`, `scripts/refindex.py`, or `scripts/index.py` separately.
