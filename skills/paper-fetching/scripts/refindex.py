#!/usr/bin/env python3
"""Build a citation-key/reference index from flattened TeX and source archives."""
import re
import sys
import tarfile
from datetime import date
from pathlib import Path

BIBITEM = re.compile(r"\\bibitem(?:\[[^]]*\])?\{([^}]+)\}")
BIBENTRY = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,")


def balanced_entry(text: str, start: int) -> str:
    opening = text.find("{", start)
    if opening < 0:
        return text[start:].strip()
    depth = 0
    escaped = False
    for pos in range(opening, len(text)):
        char = text[pos]
        if char == "{" and not escaped:
            depth += 1
        elif char == "}" and not escaped:
            depth -= 1
            if depth == 0:
                return text[start:pos + 1].strip()
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    return text[start:].strip()


def parse_bbl(text: str) -> list[tuple[str, str]]:
    matches = list(BIBITEM.finditer(text))
    entries = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find(r"\end{thebibliography}", match.end())
        if end < 0:
            end = len(text)
        entries.append((match.group(1).strip(), text[match.start():end].strip()))
    return entries


def parse_bib(text: str) -> list[tuple[str, str]]:
    matches = list(BIBENTRY.finditer(text))
    return [(match.group(1).strip(), balanced_entry(text, match.start())) for match in matches]


def selected_bbls(tex: str, names: list[str]) -> list[str]:
    requested = []
    for group in re.findall(r"\\bibliography\{([^}]+)\}", tex):
        requested.extend(part.strip().removesuffix(".bbl") for part in group.split(","))
    exact = [name for name in names if Path(name).stem in requested]
    if exact:
        return exact
    if len(names) == 1:
        return names
    main = [name for name in names if Path(name).stem == "main"]
    return main or names


def read_sources(paper_dir: Path, aid: str, tex: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    archive = paper_dir / "src" / f"{aid}.tar.gz"
    available = []
    entries = []
    if archive.is_file():
        with tarfile.open(archive, "r:gz") as tf:
            members = {member.name: member for member in tf.getmembers() if member.isfile()}
            bbls = sorted(name for name in members if name.endswith(".bbl"))
            bibs = sorted(name for name in members if name.endswith(".bib"))
            available = bbls + bibs
            for name in selected_bbls(tex, bbls):
                content = tf.extractfile(members[name]).read().decode("utf-8", errors="replace")
                entries.extend((key, entry, f"src/{aid}.tar.gz -> {name}") for key, entry in parse_bbl(content))
            if not entries:
                for name in bibs:
                    content = tf.extractfile(members[name]).read().decode("utf-8", errors="replace")
                    entries.extend((key, entry, f"src/{aid}.tar.gz -> {name}") for key, entry in parse_bib(content))
    if not entries:
        entries.extend((key, entry, f"arxiv_{aid}.tex") for key, entry in parse_bbl(tex))
    return entries, available


def build_index(paper_dir: str) -> None:
    pdir = Path(paper_dir)
    texs = sorted(pdir.glob("arxiv_*.tex"))
    lines = [f"# References index — {pdir.parent.name}", "", f"Generated {date.today()} from flattened TeX and canonical source archives.", ""]
    total = 0
    for tex_path in texs:
        aid = tex_path.stem.removeprefix("arxiv_")
        tex = tex_path.read_text(encoding="utf-8", errors="replace")
        entries, available = read_sources(pdir, aid, tex)
        lines.append(f"## {aid}")
        if available:
            files = "; ".join(f"src/{aid}.tar.gz -> {name}" for name in available)
            lines.append(f"- source files: {files}")
        if not entries:
            lines.append("_(no bibliography entries found; inspect the flattened TeX or source archive)_")
            lines.append("")
            continue
        seen = set()
        for key, entry, source in entries:
            if key in seen:
                continue
            seen.add(key)
            total += 1
            lines.extend([f"### `{key}`", f"- source: {source}", "- entry:", "```latex", entry, "```", ""])
    out = pdir / "REFERENCES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{pdir}: {total} reference entries -> {out}")


def main() -> None:
    dirs = sys.argv[1:]
    if not dirs:
        raise SystemExit("usage: refindex.py <papers_dir> [papers_dir2 ...]")
    for directory in dirs:
        build_index(directory)


if __name__ == "__main__":
    main()
