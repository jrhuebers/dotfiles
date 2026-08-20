#!/usr/bin/env python3
"""Semantic Scholar citation/reference chase for literature discovery.

Chases citations (who builds on a paper) and references (what a paper builds
on) for a set of arXiv root papers. Keyless; the working channel for
citation-following discovery. OpenAlex's ids.arxiv filter 400'd in testing —
use this instead.

Usage: python3 chase_s2.py [--direction citations|references] [--limit N] <arxiv-id>...
       (default direction: citations; default limit 100 per root)

Rate limits: ~1.2s sleep between calls; bursts hit HTTP 429 (accept partial
results and note which roots failed, or retry the failed roots after a pause).

Output: deduplicated candidate list, newest first, each with title/year/source
root. Excludes IDs listed in EXISTING (edit the set to your corpus).
"""
import json
import sys
import time
import urllib.request

UA = {"User-Agent": "research-assistant/1.0 (literature discovery)"}

# Already-in-corpus arXiv IDs to skip (edit per project)
EXISTING: set[str] = set()


def chase(aid: str, direction: str, limit: int = 100) -> list[dict]:
    url = (f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{aid}/{direction}"
           f"?fields=title,year,externalIds,abstract&limit={limit}")
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.load(r)
    except Exception as e:
        print(f"S2 {direction} {aid} FAILED: {e}", file=sys.stderr)
        return []
    out = []
    for d in res.get("data", []):
        p = d["citingPaper"] if direction == "citations" else d["citedPaper"]
        arx = (p.get("externalIds") or {}).get("ArXiv")
        if arx and arx in EXISTING:
            continue
        out.append({
            "id": arx or p.get("paperId", "?"),
            "title": p.get("title", "?"),
            "year": p.get("year"),
            "src": f"s2-{direction}:{aid}",
            "abstract": (p.get("abstract") or "")[:200],
        })
    time.sleep(1.2)
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    direction = "citations"
    limit = 100
    if "--direction" in sys.argv:
        direction = sys.argv[sys.argv.index("--direction") + 1]
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if not args:
        print(__doc__)
        return
    seen: dict = {}
    for aid in args:
        for c in chase(aid, direction, limit):
            seen[c["id"]] = c
    print(f"=== {len(seen)} unique candidates ===")
    for c in sorted(seen.values(), key=lambda x: (x["year"] or 0, x["id"]), reverse=True):
        print(f"\n[{c['year']}] {c['id']} ({c['src']})")
        print(f"  {c['title'][:110]}")
        if c["abstract"]:
            print(f"  {c['abstract'][:160]}")


if __name__ == "__main__":
    main()
