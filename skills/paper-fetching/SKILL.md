---
name: paper-fetching
description: Fetch arXiv PDFs and LaTeX sources into a verified, readable paper corpus. Use when collecting papers for research.
---

# Paper fetching

With Python 3 and `latexpand` installed, run from this skill's directory:

```bash
python3 scripts/fetch_papers.py /path/to/papers 1706.03762 1810.04805
```

Use bare arXiv IDs. The command fetches the latest PDF and original source, flattens and cleans the LaTeX, verifies the destination corpus, and builds `FIGURES.md` from figure captions. Each source-backed paper gets `arxiv_<id>.pdf`, `arxiv_<id>.tex`, and `src/<id>.tar.gz` (or the original single-file source format). If source is unavailable, it keeps the PDF with a `.source-unavailable.txt` marker.

The command never overwrites an existing paper. A fetch or QA failure exits nonzero and leaves successful downloads for inspection without rebuilding the figure index. For existing files only, run `scripts/qa_corpus.py` or `scripts/figindex.py` separately.
