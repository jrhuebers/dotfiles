#!/usr/bin/env python3
"""Build a corpus-level INDEX.md from paper-local metadata.json files."""
import json
import sys
from datetime import date
from pathlib import Path


def one_line(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def build_index(root: Path) -> None:
    rows = []
    for paper in sorted(path for path in root.iterdir() if path.is_dir()):
        metadata = paper / "metadata.json"
        if not metadata.is_file():
            continue
        record = json.loads(metadata.read_text(encoding="utf-8"))
        rows.append((record, paper.name))
    lines = ["# Paper index", "", f"Generated {date.today()} from paper-local metadata.", "", "| arXiv | Version | Title | Authors | Directory |", "|---|---|---|---|---|"]
    for record, directory in rows:
        aid = one_line(record["arxiv_id"])
        version = one_line(record["version"])
        title = one_line(record["title"])
        authors = one_line(record["authors"])
        lines.append(f"| [{aid}]({directory}/{aid}.pdf) | {version} | {title} | {authors} | `{directory}/` |")
    for record, directory in rows:
        lines.extend(["", f"## {one_line(record['arxiv_id'])}: {one_line(record['title'])}", "", f"- directory: `{directory}/`", f"- authors: {one_line(record['authors'])}", f"- version: {one_line(record['version'])}", "- abstract:", record.get("abstract", "").strip() or "_(no abstract recorded)_"])
    (root / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{root}: {len(rows)} papers -> {root / 'INDEX.md'}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: index.py <papers_dir>")
    build_index(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
