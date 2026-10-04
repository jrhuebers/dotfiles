---
name: paper-fetching
description: Fetch arXiv papers into self-contained per-paper directories with searchable figures, references, and a corpus index. Use when collecting papers for research.
---

# Paper fetching

With Python 3 and `latexpand` installed, run from this skill's directory:

```bash
python3 scripts/fetch_papers.py /path/to/papers 1706.03762 1810.04805
```

Use bare arXiv IDs. The command fetches the latest PDF and original source, flattens and cleans the LaTeX, materializes image and bibliography assets, verifies the corpus, and builds `INDEX.md` plus per-paper `FIGURES.md` and `REFERENCES.md` lookup files. As the final TeX-cleanup step, `--prune-macros=safe` (the default) searches the complete flattened source and removes unreachable ordinary top-level preamble `\def`, `\newcommand`, and `\DeclareMathOperator` declarations, including unused dependency chains. It preserves references in retained definitions and local package/class/bibliography code, `\renewcommand`, `\let`, known hooks, internal names, scoped/body declarations, and uncertain or dynamic syntax; use `--prune-macros=off` to disable pruning. This is conservative source analysis, not a guarantee of equivalent execution under arbitrary external TeX code. No macro-report file is created, and the original source is always preserved. `INDEX.md` keeps each abstract on the same physical line as `- abstract:`. It never overwrites an existing paper directory.

Image and bibliography assets retain their source-relative directory structure beneath `figures/` and `bibliography/`. During fetching, an explicit source-to-materialized-path map repairs literal TeX references (including incorrect import prefixes produced by `latexpand`) before final macro pruning. Graphics extension/search-directory precedence is preserved, duplicate basenames are never chosen arbitrarily, and unknown/dynamic references are retained conservatively. Missing literal assets produce diagnostics; ambiguous mappings fail the paper rather than silently choosing a file. Figure indexes link to the exact materialized image and identify its original archive path.

Downloads use up to five attempts for transient HTTP/network/read failures, exponential backoff with jitter, and 3.2-second request spacing. `Retry-After` seconds and HTTP dates are respected; waits over 60 seconds stop retries instead of contacting the server too early. Permanent errors and invalid/oversized payloads are not retried. Failures identify the paper and pipeline stage, while successful paper directories remain intact.

Each corpus has this structure:

```text
papers/
  INDEX.md                 # all papers: IDs, versions, titles, authors, abstracts
  <arxiv-id>/
    metadata.json          # API metadata used to regenerate INDEX.md
    <arxiv-id>.pdf
    <arxiv-id>.tex
    <arxiv-id>.tar.gz      # original source archive (or .source.tex/.tex.gz for single-file sources)
    FIGURES.md             # captions and direct materialized image paths
    REFERENCES.md          # citation keys and bibliography entries
    figures/               # extracted image assets
    bibliography/          # extracted .bib/.bbl/.bst/.bcf assets
```

Treat `papers/` as generated, read-only corpus data. Do not manually edit, delete, rename, or overwrite any PDF, TeX, archive, metadata, index, figure, or bibliography file there. To change a corpus, fetch into a new directory or use the bundled index/QA scripts to regenerate derived files.

Offline tests: `python3 -m unittest discover -s tests -v`. To additionally re-flatten and check multiple real papers from their original archives without modifying the corpus, set `PAPER_FETCHING_TEST_CORPUS=/path/to/papers` when running the tests; all regenerated TeX is written to temporary directories.

If source is unavailable, the paper directory contains the PDF, metadata, and `source-unavailable.txt` instead. A fetch or QA failure exits nonzero and leaves successful directories for inspection without rebuilding indexes. When adding papers to an existing corpus, the command retains every existing paper directory and regenerates `INDEX.md` from all paper-local metadata; do not hand-edit generated index files. For existing papers only, run `scripts/qa_corpus.py`, `scripts/figindex.py`, `scripts/refindex.py`, or `scripts/index.py` separately.
