---
name: report-writing
description: "Use when generating PDF reports from pandoc markdown."
version: 1.0.0
author: huebers
platforms: [linux]
---

# Report Writing (pandoc markdown -> PDF)

## When to Use

Generate a PDF report from markdown, especially with LaTeX math — research reports, agent-generated digests, papers.

## Tools (installed user-space, no root needed)

- pandoc at ~/.local/bin/pandoc
- tectonic at ~/.local/bin/tectonic (self-contained TeX engine; replaces a multi-GB TeX Live)

## Basic command

Canonical wrapper (thin margins + sans-serif body, tectonic engine):

    pandoc-report report.md -o report.pdf

Plain pandoc fallback (default LaTeX styling: ~2.5cm margins, serif):

    pandoc report.md -o report.pdf --pdf-engine=tectonic

## Styling (default via wrapper)

- Thin margins: `-V geometry:margin=2cm` (vs LaTeX default ~2.5cm). Override per-doc, e.g. `pandoc-report -V geometry:margin=1cm in.md -o out.pdf`.
- Sans-serif body text: header-includes `\renewcommand{\familydefault}{\sfdefault}` (Latin Modern Sans, bundled in tectonic — no system fonts needed). File: ~/.pandoc/report-sans.tex; wrapper: ~/.local/bin/pandoc-report.
- Math keeps its own (serif) math font — only ordinary text is sans.

## Markdown + LaTeX math

- Inline math: `$x^2 + y^2 = z^2$`
- Display math: `$$\mathcal{L}(\theta) = \sum_{i=1}^{n} \frac{1}{2}\|y_i - f(x_i;\theta)\|^2$$` (on its own lines)
- Full LaTeX works inside the delimiters: \frac \sum \sqrt \int \nabla \mathcal \| etc.
- Pipe tables render natively, no LaTeX needed.

## YAML front matter

    ---
    title: "Report Title"
    author: Name
    date: August 2026
    ---

## Citations (optional)

    pandoc report.md --citeproc --bibliography=refs.bib -o report.pdf --pdf-engine=tectonic

## Citation integrity rule (MANDATORY for papers/reports in agent projects)

1. Only cite papers that research-assistant has DOWNLOADED into the project
   corpus (`papers/` — check `papers/README.md` for the authoritative list
   of downloaded IDs).
2. Take ALL citation metadata (title, authors, year, arXiv ID) from the
   corpus index/notes (`papers/README.md`, `papers/notes/*.md`) — never
   invent or guess entries, and never cite from memory or web search alone.
3. Verify every `\cite` key in the paper resolves to a bib entry AND every
   bib entry corresponds to a downloaded paper: check with
   `grep -o '\\cite{[^}]*}' main.tex | tr ',' '\n' | ...` vs
   `grep -o '@[a-z]*{[^,]*' references.bib | ...` — both directions.
4. AUTHOR LISTS must be verified against the arXiv API before submission
   (first names are the classic hallucination — even corpus README entries
   can carry fabricated first names). Run the audit script
   (`scripts/audit_bib.py` in gauge-graph-network; generic version: parse
   each bib entry's arXiv ID, fetch `https://export.arxiv.org/api/query?id_list=<id>`
   with User-Agent "Mozilla/5.0" + 3.5s sleep between calls, and check every
   surname + the author count against the API names). Every entry must pass;
   a known arXiv typo (e.g. "Permultter") may be whitelisted with a comment.
5. Hallucinated citations are a paper-blocking defect. NEVER silently drop
   a citation that the text needs: send the paper to research-assistant to
   download and index first, then cite with verified provenance. Mentioning
   the line of work by name without a key is only a TEMPORARY state while
   the download is pending -- follow up and add the citation once indexed.

## Pitfalls

- FIRST compile needs internet: tectonic fetches LaTeX packages on demand, cached in ~/.cache/Tectonic. On offline compute nodes, compile on the login node or pre-warm the cache.
- --pdf-engine=tectonic is required — default engine is pdflatex, which is not installed.
- Only $...$ / $$...$$ math delimiters; pandoc's markdown reader does not parse \( \) style.
- Verified end-to-end: /tmp/math_test.md (inline + display math + table) compiles to a valid PDF.
