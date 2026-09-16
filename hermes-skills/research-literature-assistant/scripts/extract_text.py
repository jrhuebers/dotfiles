#!/usr/bin/env python3
"""Extract text from arxiv_*.pdf files in the given papers/ dirs (sibling .txt).

Usage:
    uv run --with pypdf python3 extract_text.py [dir ...]

Defaults to the three project papers dirs. Skips .txt files that already have
content (>=1000 chars). Falls back to pymupdf if pypdf is unavailable.
"""
import sys, pathlib

DEFAULT_DIRS = [
    pathlib.Path("/cephfs/users/huebers/FIM/papers"),
    pathlib.Path("/cephfs/users/huebers/diffusion-qmc/papers"),
    pathlib.Path("/cephfs/users/huebers/gauge-graph-network/papers"),
]

try:
    from pypdf import PdfReader
    HAVE = "pypdf"
except ImportError:
    try:
        import fitz  # pymupdf
        HAVE = "fitz"
    except ImportError:
        sys.exit("need pypdf or pymupdf: uv run --with pypdf python3 extract_text.py")

def extract(pdf: pathlib.Path) -> str:
    if HAVE == "pypdf":
        reader = PdfReader(str(pdf))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    doc = fitz.open(pdf)
    try:
        return "\n".join(p.get_text() for p in doc)
    finally:
        doc.close()

def main():
    dirs = [pathlib.Path(a) for a in sys.argv[1:]] or DEFAULT_DIRS
    total_ok = total_skip = total_fail = 0
    for d in dirs:
        if not d.is_dir():
            print(f"MISSING dir: {d}")
            continue
        for pdf in sorted(d.glob("arxiv_*.pdf")):
            txt = pdf.with_suffix(".txt")
            if txt.exists() and txt.stat().st_size >= 1000:
                print(f"skip {txt.name}")
                total_skip += 1
                continue
            try:
                text = extract(pdf)
                if len(text.strip()) < 500:
                    print(f"WARN low text ({len(text)} chars): {pdf.name}")
                txt.write_text(text)
                print(f"OK {txt.name} ({len(text)} chars)")
                total_ok += 1
            except Exception as e:
                print(f"FAIL {pdf.name}: {e}")
                total_fail += 1
    print(f"\n{total_ok} extracted, {total_skip} skipped, {total_fail} failed")

if __name__ == "__main__":
    main()
