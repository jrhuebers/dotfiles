#!/usr/bin/env python3
"""Verify fetched arXiv paper artifacts; nonzero exit if any paper fails."""
import argparse
from pathlib import Path
import re
import tarfile


def check_paper(directory: Path, aid: str, version: str | None = None) -> list[str]:
    errors = []
    pdf = directory / f"arxiv_{aid}.pdf"
    tex = directory / f"arxiv_{aid}.tex"
    originals = list((directory / "src").glob(f"{aid}.*")) if (directory / "src").is_dir() else []
    marker = directory / f"arxiv_{aid}.source-unavailable.txt"
    if not pdf.is_file() or pdf.stat().st_size < 10_000:
        errors.append("missing/invalid PDF")
    else:
        with pdf.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                errors.append("missing/invalid PDF")
    if marker.exists():
        record = marker.read_text(encoding="utf-8")
        if not re.search(rf"^arXiv {re.escape(version) if version else re.escape(aid) + 'v[0-9]+'} \| source unavailable", record):
            errors.append("PDF-only marker has missing/wrong version")
        if tex.exists() or originals:
            errors.append("PDF-only marker contradicts source artifacts")
        return errors
    if not tex.is_file() or tex.stat().st_size < 200:
        errors.append("missing/tiny flattened TeX")
    else:
        text = tex.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"\\documentclass(?:\[[^]]*\])?\s*\{", text):
            errors.append("missing documentclass")
        if not re.search(rf"^% arXiv {re.escape(aid)} \(latest: {re.escape(version) if version else re.escape(aid) + 'v[0-9]+'}\)", text):
            errors.append("missing/mismatched version header")
        if re.search(r"\\(?:input|include)\s*\{[^}]+\}", text):
            errors.append("unexpanded TeX input/include")
    if len(originals) != 1 or originals[0].stat().st_size == 0:
        errors.append("missing or ambiguous original source")
    elif originals[0].name.endswith(".tar.gz"):
        try:
            with tarfile.open(originals[0], "r:gz") as tf:
                if not tf.getmembers():
                    errors.append("empty source archive")
        except tarfile.TarError:
            errors.append("invalid source archive")
    return errors


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    args = p.parse_args()
    aids = {p.stem.removeprefix("arxiv_") for p in args.directory.glob("arxiv_*.pdf")}
    aids.update(p.stem.removeprefix("arxiv_") for p in args.directory.glob("arxiv_*.tex"))
    if not aids:
        p.error("no arxiv_*.pdf or arxiv_*.tex files found")
    failed = False
    for aid in sorted(aids):
        errors = check_paper(args.directory, aid)
        print(f"{aid}: {'FAIL: ' + '; '.join(errors) if errors else 'OK'}")
        failed |= bool(errors)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
