---
name: pandoc-pdf
description: Use when generating PDFs from Markdown with LaTeX math.
---

# pandoc → PDF (Markdown with LaTeX math)

Generate report PDFs from Markdown containing $...$ / $$...$$ math. Fully doable without root: both pandoc and tectonic install into ~/.local/bin. Primary use case here: research agents emitting report PDFs from markdown. User-space install (no root / HPC login node) covered below.

## Check what's already there
`which pandoc pdflatex xelatex lualatex tectonic` — any LaTeX engine works; tectonic is the lightweight default on this box (already installed, see memory). ~/.local/bin is on PATH.

## User-space install (no root, HPC login node)
1. Resolve latest versions from GitHub API:
   - pandoc: `curl -s https://api.github.com/repos/jgm/pandoc/releases/latest | grep browser_download_url.*linux-amd64`
   - tectonic: `curl -s https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest | grep browser_download_url.*x86_64-unknown-linux-gnu`
2. `curl -sL -o` the tarballs to /tmp, extract, `cp` the binaries to ~/.local/bin, `chmod +x`, then `hash -r` (shell may have cached "not found").
3. Why tectonic: single self-contained binary (~20 MB); fetches LaTeX packages on demand from the bundle server and caches them in ~/.cache/Tectonic. Avoids a multi-GB TeX Live install and any apt/root dependency. Drops straight into pandoc's engine slot.

## Compile
```
pandoc report.md -o report.pdf --pdf-engine=tectonic
```
- YAML front matter (title/author/date) renders as the title block automatically.
- Citations: add `--citeproc` — pandoc builds the bibliography itself, so no biber needed.
- Styling: `--template=<file>` for custom LaTeX templates; `--reference-doc=<docx>` for the office-format route.

## Verify the output (important pitfall)
- Check exit code AND inspect the file: `file out.pdf` should say "PDF document, version 1.5".
- Tectonic/pandoc emit COMPRESSED object streams: grepping raw bytes for `/Type /Page` or `/FontFile` returns 0 matches even on a perfectly valid PDF — that is a false negative, NOT corruption. Don't chase it.
- Reliable byte-level checks: `data.rstrip().endswith(b'%%EOF')` and `b'startxref' in data`; plus `file` for the type.

## Pitfalls
- First compile needs internet (tectonic package fetch). Pre-warm ~/.cache/Tectonic before running on compute nodes without network, or ship the cache.
- Non-zero exit from pandoc/tectonic = the LaTeX failed to compile — usually a math syntax error in the markdown; fix the math, not the toolchain.
- Install artifacts live in /tmp during setup; clean up the tarballs afterward.
