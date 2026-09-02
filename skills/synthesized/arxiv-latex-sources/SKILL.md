---
name: arxiv-latex-sources
description: "Fetch and process arXiv LaTeX source: e-print tarballs, flatten/strip .tex for LLM reading, figure-caption index. Use when a paper needs machine-perfect math/tables (source > OCR > pypdf)."
author: huebers
---

# arXiv LaTeX Source Extraction & Corpus Building

Fetch author-uploaded LaTeX source of arXiv papers (the ground truth the PDF was
compiled from), flatten/strip it for LLM consumption, and build a per-paper corpus.

## When to use

- A paper corpus needs machine-perfect math/tables (OCR and pypdf degrade math; source does not).
- User asks for `.tex` sources, "raw latex", "the actual source", citation keys, or version-diffable content.
- Deliverable layout per paper: `<id>.pdf` + `<id>.tex` (flattened+stripped) + `src/` (original tarball, canonical).

## Fetch (always the LATEST version)

```bash
curl -sL -A "research-assistant/0.1" https://arxiv.org/e-print/<id> -o <id>.tar.gz
```

- Bare ID (NO version suffix) = latest version. Record the concrete version via the API:
  `https://export.arxiv.org/api/query?id_list=<id>` → `<id>` field shows e.g. `2512.00242v3`.
- Rate limit ~1 req/3s with an identifying User-Agent (arXiv policy).
- Content types: tar.gz (typical: .tex + figures + .bbl/.bib + bundled .cls/.sty),
  single .tex.gz, raw .tex, ancient .ps. Detect via magic bytes (gzip `1f8b`, PDF `%PDF`, PS `%!`).
- Safe-extract: skip absolute paths and `..` components (arXiv sanitizes, but guard anyway).
- `scripts/fetch_arxiv_src.py` — batch fetcher with content sniffing + rate limiting.

## Inspect before processing

- Main file = the .tex containing `\documentclass` — names vary wildly (main.tex,
  paper.tex, VDMv3.tex, neurips_2026_preprint.tex, ICLR2024.tex...). Search all .tex in the tree; don't guess.
- Measured on 18 real papers: 100% source availability (even 2011-2012 submissions),
  0-64 .tex files, 0-541 figures, `\newcommand` density median 8 (max 49) per main.
- 17/18 strict UTF-8 (the latin1 stragglers need `errors=replace`).
- Not all papers have source (some authors suppress it); always keep the PDF as fallback ground truth.

## Token economics: raw .tex over pandoc markdown

cl100k measurements across 18 papers: flattened .tex ≈ 1.13x (median) / 1.38x (total)
the pandoc markdown tokens — in ~1/3 of papers the markdown is BIGGER (pandoc adds
`:::` fenced divs, pipe tables, headers). **Raw .tex is the primary LLM-reading
format**; do not default to pandoc.

### pandoc reliability pitfalls (17/18 clean)

- **Infinite hang**: pandoc's LaTeX reader parses bundled `.sty` files found via cwd.
  AAAI 2027's .sty (nested `\AtBeginDocument`) makes pandoc 3.x loop forever. FIX:
  strip `\usepackage`/`\RequirePackage` first: `sed -E '/^\s*\\(usepackage|RequirePackage)/d' main.tex`
- `\input`/`\include` resolve ONLY when pandoc runs FROM main.tex's directory; wrong
  cwd silently drops content.
- Author-source errors (stray `}` after `\end{align}`) break pandoc but not LaTeX (~1/18).

## Flattening + comment stripping

- Flatten: resolve `\input`/`\include` recursively (subdirs + `.tex` suffix). Regex
  resolution is fine for READING (all chapters/sections land); `latexpand` is the
  compile-grade alternative. Mark unresolved inputs with `% UNRESOLVED` (check on
  pre-strip output — markers vanish if stripping runs after).
- Strip comments with a VERBATIM-AWARE stripper: `%` outside
  verbatim/lstlisting/comment/minted envs; preserve `\%` escapes. Cuts 1-20% of chars.
- ALWAYS keep the original tarball as canonical; the flattened .tex is a derived
  artifact with a header stamping: arxiv id, latest version, tool, fetch date.
- `scripts/texflatten.py` — find-main → flatten → verbatim-aware strip → version-stamped header.

## Corpus policy

1. Raw .tex (flattened, comment-stripped) = primary reading format.
2. PDF ALWAYS downloaded alongside (human ground truth).
3. ALWAYS latest arXiv version (bare-ID e-print + recorded version check).
4. Per-paper: `<id>.pdf` + `<id>.tex` + `src/` (tarball).

## Figure caption index — figures as LLM-searchable TEXT

Every figure has a text caption; a text-only model cannot see image bytes but CAN
read captions. `scripts/figindex.py` parses the flattened .tex corpus and writes
`FIGURES.md`:

```
### Figure 3 (fig:architecture)
- image: src/2401.00012.tar.gz -> figures/arch.pdf
- caption: Overview of the proposed architecture. We ...
```

Per figure: source-order number, LaTeX `\label`, includegraphics target annotated
with its `src/<id>.tar.gz` path, and full caption text (brace-matched; multi-line +
math intact). Edge cases verified on 457 real figures:
- Multi-image figures joined with `; `.
- Subfigure-only composites (no top-level caption → flagged).
- TikZ-drawn figures (`\begin{tikzpicture}` inside figure env, NO external file →
  correctly reported as no includegraphics; rendering needs pdflatex before vision).

## Citation & metadata verification (anti-hallucination)

Author lists, titles, and arXiv IDs in ANY index/README/bib MUST come from the arXiv
API or the paper's own `bibliography.bib` — never from memory. Plausible-but-wrong
IDs (real arXiv IDs of the WRONG paper) are the #1 failure mode when agents suggest citations.

- Verify by TITLE + AUTHORS via the API, never by ID alone.
- Batched id_list queries need `&max_results=100` — the default (10) silently drops rows.
- For benchmark-baseline rows: extract the paper's own `bibliography.bib` from `src/<id>.tar.gz`.
- API-side typos exist (2209.00546 lists 'Permultter'; real name Perlmutter) — keep
  an exception map in the audit script, don't "fix" the README.
- Expand `et al.` to full API author lists; never leave an unverifiable abbreviation.
- `scripts/audit_readme_authors.py` re-verifies every README row against the API
  (surname-set containment, batched). Run before any submission or bib export.

## Pitfalls recap

- Bundled .sty → pandoc hang; strip `\usepackage` first.
- cwd matters for `\input` resolution.
- Version suffixes: bare-ID fetch gets latest; record the actual version.
- Old papers may be latin1/mixed encoding.
- Figure CONTENT (pixels) is never in .tex — but figure CAPTIONS are; run
  `scripts/figindex.py` to make them searchable text before resorting to vision/OCR.
