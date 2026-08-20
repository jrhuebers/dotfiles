#!/usr/bin/env python3
"""Fetch arXiv e-print (LaTeX source) packages for a list of IDs into a dir.

arXiv e-print endpoint: https://arxiv.org/e-print/<id>  (bare ID = LATEST version)
Returns: tar.gz (typical), .tex.gz (single file), .tex (raw), .ps (ancient).
Rate limit: 1 req / 3s, with identifying User-Agent (arXiv policy).
Usage: fetch_arxiv_src.py <outdir> <id1> [id2 ...]
"""
import sys, os, time, urllib.request

UA = "research-assistant/0.1 (literature curation; contact: jrhuebers@gmail.com)"

def fetch(aid, outdir):
    url = f"https://arxiv.org/e-print/{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        ext = "bin"
        if data[:2] == b"\x1f\x8b":
            ext = "gz"
        elif data[:4] == b"\x25\x50\x44\x46":
            ext = "pdf"
        elif data[:2] == b"\x25\x21":
            ext = "ps"
        elif data[:5] == b"\\docu" or data[:4] == b"%\\":
            ext = "tex"
        path = os.path.join(outdir, f"{aid}.{ext}")
        with open(path, "wb") as f:
            f.write(data)
        return ext, len(data)
    except Exception as e:
        return f"ERR:{type(e).__name__}:{e}", 0

def main():
    outdir = sys.argv[1]
    ids = sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)
    for aid in ids:
        ext, n = fetch(aid, outdir)
        print(f"{aid}: {ext} {n/1024:.1f} KB")
        time.sleep(3.2)

if __name__ == "__main__":
    main()
