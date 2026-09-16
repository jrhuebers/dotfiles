---
name: arxiv-latex-sources
description: "Use when fetching or processing arXiv LaTeX sources."
version: 1.0.0
author: curator
platforms: [linux, macos]
---

# arXiv LaTeX Source Extraction & Corpus Building

Fetch the author-uploaded LaTeX source of arXiv papers (the ground truth the
PDF was compiled from), flatten/strip it for LLM consumption, and build the
per-paper corpus. Complements the `arxiv` skill (search/metadata/PDF), which is
bundled and cannot be edited — this skill carries the source-level workflow.

## When to use

- A paper corpus needs machine-perfect math/tables (OCR and pypdf text both
  degrade math; source does not).
- The user asks for `.tex` sources, "raw latex", "the actual source", or wants
  citation keys, or version-diffable content.
- Deliverable layout per paper: `<id>.pdf` + `<id>.tex` (flattened+stripped,
  derived) + `src/` (original tarball, canonical).

## Fetch (always the LATEST version)

```bash
curl -sL -A "research-assistant/0.1" https://arxiv.org/e-print/<id> -o <id>.tar.gz
```

- Bare ID (NO version suffix) = latest version. Record the concrete version via
  the API so the corpus is traceable:
  `https://export.arxiv.org/api/query?id_list=<id>` -> `<id>` field shows e.g.
  `2512.00242v3`.
- Rate limit ~1 req/3s with an identifying User-Agent (arXiv policy).
- Content types: tar.gz (typical; .tex + figures + .bbl/.bib + bundled
  .cls/.sty), single .tex.gz, raw .tex, ancient .ps. Detect via magic bytes
  (gzip `1f8b`, PDF `%PDF`, PS `%!`).
- Safe-extract: skip absolute paths and `..` components (arXiv sanitizes, but
  guard anyway).
- `scripts/fetch_arxiv_src.py` — batch fetcher with content sniffing + rate
  limiting.

## Inspect before processing

- Main file = the .tex containing `\documentclass` — names vary wildly
  (main.tex, paper.tex, VDMv3.tex, neurips_2026_preprint.tex, ICLR2024.tex,
  qmc_nf_arxiv_1.tex, tippfn.tex...). Search all .tex in the tree, don't guess.
- Measured on 18 real papers (2026-08): 100% source availability (even
  2011-2012 submissions), 0-64 .tex files, 0-541 figures, `\newcommand`
  density median 8 (max 49) per main, comment density median 0.2% (max 4.9%),
  17/18 strict UTF-8 (the latin1 stragglers need errors=replace).
- Not all papers have source (some authors suppress it); availability is high
  but not universal — always keep the PDF as the fallback ground truth.

## Token economics (why raw .tex over pandoc markdown)

cl100k measurements across 18 papers: flattened .tex ≈ 1.13x (median) / 1.38x
(total) the pandoc markdown tokens — and in ~1/3 of papers the markdown is
BIGGER (pandoc adds `:::` fenced divs, pipe tables, headers, brackets). Markdown
conversion buys almost nothing in tokens and costs fidelity. User verdict
(2026-08): pandoc output "doesn't look that great" — **raw .tex is the primary
LLM-reading format**; do not default to pandoc.

## pandoc tex→markdown reliability (18 tested: 17/18 clean)

- PITFALL (infinite hang): pandoc's LaTeX reader parses bundled `.sty` files
  found via cwd. AAAI 2027's .sty (nested `\AtBeginDocument` hooks) makes
  pandoc 3.x loop forever — deterministic, cwd-dependent (paper dir = hang,
  elsewhere = fine). FIX: strip `\usepackage`/`\RequirePackage` lines first:
  `sed -E '/^\s*\\(usepackage|RequirePackage)/d' main.tex`
- `\input`/`\include` resolve ONLY when pandoc runs FROM the main.tex's
  directory; wrong cwd silently drops content (one multi-file paper produced
  1 byte of output).
- Author-source errors (e.g. NCF 2405.02154: stray `}` after `\end{align}`)
  break pandoc but not LaTeX — ~1/18; handle tolerantly or skip to raw tex.

## Flattening + comment stripping

- Flatten (resolve `\input`/`\include` recursively, subdirs + `.tex` suffix):
  regex resolution is fine for READING (verified: all chapters/sections land,
  incl. tricky names like `1.5_problem_setup`); `latexpand` is the
  compile-grade alternative. Mark unresolved inputs with a `% UNRESOLVED`
  comment (note: such markers vanish if comment-stripping runs after — do
  resolution checks on the pre-strip output).
- Strip comments with a VERBATIM-AWARE stripper: `%` outside
  verbatim/lstlisting/comment/minted envs; preserve `\%` escapes. Cuts 1-20%
  of chars and removes author chatter/TODOs.
- ALWAYS keep the original tarball as canonical; the flattened .tex is a
  derived artifact with a header stamping: arxiv id, latest version, tool,
  fetch date. This makes the transformation zero-risk.
- `scripts/texflatten.py` — find-main → flatten → verbatim-aware strip →
  version-stamped header (API version check included).

## Corpus policy (user's standing preferences, 2026-08)

1. Raw .tex (flattened, comment-stripped) = primary reading format.
2. PDF ALWAYS downloaded alongside (human ground truth).
3. ALWAYS latest arXiv version (bare-ID e-print + recorded version check).
4. Per-paper: `<id>.pdf` + `<id>.tex` + `src/` (tarball).

## Figure caption index — figures as LLM-searchable TEXT

- Figures are ALREADY stored in any tex corpus: inside `src/` tarballs and
  rendered in the PDFs. The gap is LLM-accessibility, not storage — a
  text-only model cannot see image bytes, but every figure has a text caption.
- `scripts/figindex.py` parses the flattened .tex corpus and writes
  `papers/FIGURES.md`: per figure — source-order number, LaTeX \label,
  includegraphics target annotated with its `src/<id>.tar.gz` path (so a
  future vision pass locates the file without re-extracting), and the full
  caption text (brace-matched; multi-line + math intact).
- Edge cases verified on 457 real figures: multi-image figures (joined with
  `; `), subfigure-only composites (no top-level caption -> flagged), and
  TikZ-drawn figures (`\begin{tikzpicture}` inside the figure env, NO external
  file -> correctly reported as no includegraphics; rendering them needs
  pdflatex before any vision pass).
- Text-only-model verdict (2026-08): the caption index makes "what does
  Figure 3 show" answerable without vision. Actual image CONTENT reading
  requires either the dots.ocr VLM (below) or a vision-capable API provider.

## Citation & metadata verification (anti-hallucination rule)

Author lists, titles, and arXiv IDs in ANY index/README/bib MUST come from the
arXiv API or the paper's own `bibliography.bib` — never from memory. Concrete
failure (2026-08): BuNN (2405.15540) was indexed as 'Hansen, Gebhart' from
memory (conflated with the SheafNN paper 2012.06333, which IS Hansen &
Gebhart); the API says Bamberger, Barbero, Dong, Bronstein. The same session
caught wrong IDs from three external models — plausible-but-wrong IDs are the
#1 failure mode when agents or LLMs suggest citations.

- Verify by TITLE + AUTHORS via the API, never by ID alone.
- Batched id_list queries need `&max_results=100` — the default caps at 10 and
  silently drops rows (first audit run missed half the corpus this way).
- For benchmark-baseline rows, the paper's own src tarball `bibliography.bib`
  is ground truth for exact titles (extract from `src/<id>.tar.gz`).
- API-side typos exist (2209.00546 lists 'Permultter'; real name Perlmutter) —
  exception-map known cases in the audit script, don't "fix" the README.
- Expand `et al.` to full API author lists in indexes; never leave an
  unverifiable abbreviation.
- `scripts/audit_readme_authors.py` re-verifies every README row against the
  API (surname-set containment, batched); run before any submission or bib
  export. Case log + full rules: `references/citation-verification.md`.

## Pitfalls recap

- Bundled .sty → pandoc hang; strip usepackage first.
- cwd matters for \input resolution.
- Version suffixes: bare-ID fetch gets latest; record the actual version.
- Old papers may be latin1/mixed encoding.
- Figure CONTENT (pixels) is never in .tex — but figure CAPTIONS are; run
  `scripts/figindex.py` to make them searchable text before resorting to
  vision/OCR
  (dots.ocr markdown embeds them; see `references/dots-ocr-gpu.md` for the
  validated GPU VLM OCR pipeline: setup, the two transformers 4.56.1 blockers
  — video_processor=None and the chat_template.json source — and the
  prompt_layout_all_en recipe giving LaTeX math + HTML tables + images).

## Support files

- `references/dots-ocr-gpu.md` — dots.ocr VLM OCR on GPU (math+tables+figures).
- `references/citation-verification.md` — anti-hallucination rules + wrong-ID case log.
- `scripts/texflatten.py` — flatten + verbatim-aware comment strip + version header.
- `scripts/fetch_arxiv_src.py` — rate-limited e-print batch fetcher.
- `scripts/figindex.py` — figure-caption index (FIGURES.md) from the flattened corpus.
- `scripts/audit_readme_authors.py` — re-verify every README author list against the arXiv API.
