#!/usr/bin/env python3
"""Build a figure-caption index from a flattened .tex corpus.

For each papers dir: parse arxiv_<id>.tex (or any *_*.tex), find figure environments,
extract (source-order number, label, includegraphics target, caption text),
and write FIGURES.md next to the corpus.

Captions are text, so this makes every figure searchable/quotable by a
text-only LLM. The includegraphics target + src tarball path let a future
vision pass locate the actual image file.

Validated on 457 real figures: multi-image figures joined with "; ",
subfigure-only composites flagged as no-caption, TikZ-drawn figures correctly
reported as no external file.

Usage: python3 figindex.py <papers_dir> [papers_dir2 ...]
"""
import os
import re
import sys
import glob
from datetime import date


def brace_match(text, start):
    """Index of matching '}' for the '{' at text[start]; -1 if unbalanced."""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def strip_tex_noise(s):
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_figures(tex):
    figs = []
    env_re = re.compile(r"\\begin\{(figure\*?)\}(.*?)\\end\{\1\}", re.S)
    for m in env_re.finditer(tex):
        body = m.group(2)
        incs = [p.strip() for p in
                re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", body)]
        capm = re.search(r"\\caption(?:\[[^\]]*\])?\{", body)
        caption = ""
        if capm:
            end = brace_match(body, capm.end() - 1)
            if end != -1:
                caption = strip_tex_noise(body[capm.end():end])
        labm = re.search(r"\\label\{([^}]*)\}", body)
        figs.append({
            "includegraphics": incs,
            "caption": caption,
            "label": labm.group(1) if labm else "",
        })
    return figs


def main():
    dirs = sys.argv[1:]
    if not dirs:
        sys.exit("usage: figindex.py <papers_dir> [papers_dir2 ...]")
    for pdir in dirs:
        texs = sorted(glob.glob(os.path.join(pdir, "arxiv_*.tex")))
        if not texs:
            texs = sorted(glob.glob(os.path.join(pdir, "*.tex")))
        if not texs:
            print(f"{pdir}: no tex files, skipped")
            continue
        proj = os.path.basename(os.path.dirname(pdir))
        lines = [f"# Figures index — {proj}",
                 "",
                 f"Generated {date.today()} from flattened .tex sources. Figure N "
                 "= source order, not LaTeX numbering. includegraphics target + "
                 "src tarball locate the actual image file.",
                 ""]
        total = nocap = noinc = 0
        for tex_path in texs:
            base = os.path.basename(tex_path)
            pid = base[:-4] if base.endswith(".tex") else base
            if base.startswith("arxiv_"):
                pid = base[6:-4]
            with open(tex_path, encoding="utf-8", errors="replace") as f:
                tex = f.read()
            figs = parse_figures(tex)
            total += len(figs)
            lines.append(f"## {pid}")
            if not figs:
                lines.append("_(no figure environments found)_")
                lines.append("")
                continue
            for i, fig in enumerate(figs, 1):
                if not fig["caption"]:
                    nocap += 1
                if not fig["includegraphics"]:
                    noinc += 1
                tgt = "; ".join(fig["includegraphics"]) if fig["includegraphics"] else "_(none)_"
                tarball = f"src/{pid}.tar.gz -> " if os.path.exists(
                    os.path.join(pdir, "src", f"{pid}.tar.gz")) else ""
                label = f" ({fig['label']})" if fig["label"] else ""
                lines.append(f"### Figure {i}{label}")
                lines.append(f"- image: {tarball}{tgt}")
                lines.append(f"- caption: {fig['caption'] or '_(no caption)_'}")
            lines.append("")
        out = os.path.join(pdir, "FIGURES.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"{pdir}: {total} figures across {len(texs)} papers -> {out}")
        print(f"   (no caption: {nocap}, no includegraphics: {noinc})")


if __name__ == "__main__":
    main()
