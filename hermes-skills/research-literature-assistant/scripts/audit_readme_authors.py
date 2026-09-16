#!/usr/bin/env python3
"""Audit README author lists against the arXiv API (batched id_list queries).

Checks every `arxiv_<id>.pdf` row in each project's papers/README.md: fetches
the API author list (full names) and compares surname sequences with the
README's author field. Reports mismatches. The rule this enforces: bibliographic
metadata comes from the API, never from memory (research-literature-assistant
skill, "Bibliographic metadata: verify, never invent").

Usage: python3 audit_readme_authors.py [readme_path ...]
Defaults: FIM, diffusion-qmc, gauge-graph-network papers/README.md

Batch gotcha handled: arXiv id_list queries return at most 10 entries unless
max_results is raised (this script passes max_results=100).
"""
import re
import time
import urllib.request

UA = {"User-Agent": "research-assistant/1.0 (citation audit)"}

README_PATHS = [
    "/cephfs/users/huebers/FIM/papers/README.md",
    "/cephfs/users/huebers/diffusion-qmc/papers/README.md",
    "/cephfs/users/huebers/gauge-graph-network/papers/README.md",
]

ROW_RE = re.compile(r"^\|\s*arxiv_(\d{4}\.\d{4,5})\.pdf\s*\|\s*([^|]*?)\s*\|\s*\1\s*\|", re.M)

# Known API-side typos: arXiv itself misspells these; the README is correct.
API_TYPO_FIXES = {
    "2209.00546": {"permultter": "perlmutter"},  # real: Michael Perlmutter (UCLA)
}


def fetch_authors(aids):
    """Return {aid: [full names]} for a list of arXiv IDs (one batched query)."""
    url = ("https://export.arxiv.org/api/query?id_list=" + ",".join(aids)
           + "&max_results=100")
    req = urllib.request.Request(url, headers=UA)
    xml = urllib.request.urlopen(req, timeout=60).read().decode()
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
    out = {}
    for e in entries:
        idm = re.search(r"<id>http://arxiv.org/abs/([^v]+)", e)
        names = re.findall(r"<name>(.*?)</name>", e)
        if idm:
            out[idm.group(1)] = names
    return out


def surname(name):
    parts = name.split()
    return parts[-1].lower() if parts else ""


def main():
    paths = README_PATHS
    import sys
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rows = ROW_RE.findall(text)
        print(f"=== {path} ({len(rows)} arxiv rows) ===")
        for i in range(0, len(rows), 20):
            batch = rows[i:i + 20]
            try:
                api = fetch_authors([a for a, _ in batch])
            except Exception as e:
                print(f"  batch FAIL {e}")
                time.sleep(3.1)
                continue
            for aid, author_field in batch:
                auth_part = author_field.split("*")[0].strip()
                readme_surnames = [surname(p) for p in auth_part.replace(" and ", ",").split(",") if p.strip()]
                api_names = api.get(aid, [])
                api_surnames = [surname(n) for n in api_names]
                if aid in API_TYPO_FIXES:
                    api_surnames = [API_TYPO_FIXES[aid].get(s, s) for s in api_surnames]
                if readme_surnames and api_surnames:
                    extra = [s for s in readme_surnames if s not in api_surnames]
                    if extra:
                        print(f"  MISMATCH {aid}: README surnames NOT in API: {extra}")
                        print(f"    README: {readme_surnames}")
                        print(f"    API:    {api_names}")
                elif not api_names:
                    print(f"  {aid}: no API entry")
            time.sleep(3.1)


if __name__ == "__main__":
    main()
