#!/usr/bin/env python3
"""Flatten an extracted arXiv source tree using latexpand, with a traceable header."""
import argparse
from datetime import date
from pathlib import Path
import re
import shutil
import subprocess

VERBATIM = {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "alltt"}
TOKEN = re.compile(r"\\(?:begin|end)\{([A-Za-z*]+)\}|%")
DOC = re.compile(r"^[^%\n]*\\documentclass(?:\[[^]]*\])?\s*\{", re.M)


def strip_comments(text: str) -> str:
    """Strip ordinary comments; preserve escaped percent and verbatim blocks."""
    out = []
    verbatim = None
    for line in text.splitlines(keepends=True):
        pos = 0
        for match in TOKEN.finditer(line):
            token = match.group()
            if token.startswith(r"\begin{") and match.group(1) in VERBATIM and verbatim is None:
                verbatim = match.group(1)
            elif token.startswith(r"\end{") and match.group(1) == verbatim:
                verbatim = None
            elif token == "%" and verbatim is None:
                # Even runs of backslashes escape '%' only when odd.
                backslashes = len(line[:match.start()]) - len(line[:match.start()].rstrip("\\"))
                if backslashes % 2 == 0:
                    out.append(line[pos:match.start()] + ("\n" if line.endswith("\n") else ""))
                    break
        else:
            out.append(line[pos:])
    return "".join(out)


def collapse_blank_lines(text: str) -> str:
    """Reduce outside-code runs of blank lines to one; preserve verbatim contents."""
    out = []
    verbatim = None
    blank_lines = 0
    for line in text.splitlines(keepends=True):
        was_verbatim = verbatim is not None
        for match in TOKEN.finditer(line):
            token = match.group()
            if token.startswith(r"\begin{") and match.group(1) in VERBATIM and verbatim is None:
                verbatim = match.group(1)
            elif token.startswith(r"\end{") and match.group(1) == verbatim:
                verbatim = None
        if was_verbatim or verbatim is not None:
            blank_lines = 0
            out.append(line)
        elif not line.strip():
            blank_lines += 1
            if blank_lines <= 1:
                out.append(line)
        else:
            blank_lines = 0
            out.append(line)
    return "".join(out)


def find_main(root: Path) -> Path:
    candidates = []
    for path in root.rglob("*.tex"):
        if path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if DOC.search(text):
            candidates.append((path.stat().st_size, path))
    if not candidates:
        raise ValueError("no LaTeX main file containing \\documentclass")
    return max(candidates)[1]


def flatten(root: Path, aid: str, version: str, output: Path) -> Path:
    tool = shutil.which("latexpand")
    if not tool:
        raise RuntimeError("latexpand is required (install via TeX Live or CTAN)")
    main = find_main(root)
    # --empty-comments destroys literal % inside verbatim; keep comments until our verbatim-aware pass.
    run = subprocess.run([tool, "--keep-comments", main.name], cwd=main.parent, capture_output=True, timeout=120, check=False)
    if run.returncode or not run.stdout:
        raise RuntimeError(f"latexpand failed: {run.stderr.decode(errors='replace')[:1000]}")
    # Missing includes sometimes only yield warnings and still exit successfully.
    warnings = run.stderr.decode(errors="replace")
    if re.search(r"(?:not found|cannot open|no such file|can't open)", warnings, re.I):
        raise RuntimeError(f"latexpand unresolved input: {warnings[:1000]}")
    clean = collapse_blank_lines(strip_comments(run.stdout.decode("utf-8", errors="replace")))
    if not DOC.search(clean) or len(clean) < 200:
        raise ValueError("flattened LaTeX is empty or missing documentclass")
    header = (f"% arXiv {aid} (latest: {version}) | flattened+comments-stripped+blank-lines-collapsed by latexpand --keep-comments + flatten_tex.py\n"
              f"% main: {main.relative_to(root)} | fetched: {date.today().isoformat()}\n")
    output.write_text(header + clean, encoding="utf-8")
    return main


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("id")
    p.add_argument("version")
    p.add_argument("output", type=Path)
    args = p.parse_args()
    print(f"main: {flatten(args.source.resolve(), args.id, args.version, args.output)}")


if __name__ == "__main__":
    main()
