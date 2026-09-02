#!/usr/bin/env python3
"""Audit README author lists against the arXiv API (batched id_list queries).

For every `arxiv_<id>.pdf` row in each papers/README.md: fetch the API author
list (full names) and compare surname sets with the README's author field.
Report mismatches; never fill names in by hand (rule: metadata comes from the
API, never from memory).

Usage: python3 audit_readme_authors.py [README.md ...]
Defaults: the three project corpora (FIM, diffusion-qmc, gauge-graph-network).
"""
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "research-assistant/1.0 (citation audit)"}

README_PATHS = [
    "/cephfs/users/huebers/FIM/papers/README.md",
    "/cephfs/users/huebers/diffusion-qmc/papers/README.md",
    "/cephfs/users/huebers/gauge-graph-network/papers/README.md",
]

ROW_RE = re.compile(r"^\|\s*arxiv_(\d{4}\.\d{4,5})\.pdf\s*\|\s*([^|]*?)\s*\|\s*\1\s*\|", re.M)

# Known API-side typos (the API itself is wrong; the README is right).
API_TYPO_FIXES = {
    "2209.00546": {"permultter": "perlmutter"},  # real name: Michael Perlmutter
}


def fetch_authors(aids):
    """Return {aid: [full names]} — batched; max_results=100 is REQUIRED
    (the id_list default of 10 silently drops rows)."""
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
    paths = sys.argv[1:] if len(sys.argv) > 1 else README_PATHS
    problems = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            print(f"skip {path}: not found")
            continue
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
                readme_surnames = [surname(p) for p in
                                   auth_part.replace(" and ", ",").split(",")
                                   if p.strip()]
                api_names = api.get(aid, [])
                api_surnames = [surname(n) for n in api_names]
                if aid in API_TYPO_FIXES:
                    api_surnames = [API_TYPO_FIXES[aid].get(s, s) for s in api_surnames]
                if readme_surnames and api_surnames:
                    extra = [s for s in readme_surnames if s not in api_surnames]
                    if extra:
                        problems += 1
                        print(f"  MISMATCH {aid}: README surnames NOT in API: {extra}")
                        print(f"    README: {readme_surnames}")
                        print(f"    API:    {api_names}")
                elif not api_names:
                    print(f"  {aid}: no API entry (check max_results / ID validity)")
            time.sleep(3.1)  # arXiv etiquette
    print(f"\n{problems} mismatch(es). Fix README rows from the API output; "
          "never edit names from memory.")


if __name__ == "__main__":
    main()
