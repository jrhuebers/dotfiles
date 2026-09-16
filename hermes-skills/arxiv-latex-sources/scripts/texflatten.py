#!/usr/bin/env python3
"""Flatten an arXiv LaTeX source tree into ONE .tex file, stripping comments.

- resolves \\input{...} / \\include{...} recursively (subdirs, .tex suffix)
- strips % comments EXCEPT inside verbatim/lstlisting/comment environments
  and except escaped \\%
- marks unresolved includes with a % UNRESOLVED comment (check BEFORE stripping)
- writes a traceability header (arxiv id, latest version via API, source files)
- usage: texflatten.py <src-tree-dir> <arxiv-id> -o <out.tex>
"""
import os, re, sys, urllib.request, datetime

VERBATIM_ENVS = {"verbatim", "lstlisting", "verbatim*", "minted", "alltt", "Verbatim"}

def latest_version(aid):
    try:
        req = urllib.request.Request(f"https://export.arxiv.org/api/query?id_list={aid}",
                                     headers={"User-Agent": "research-assistant/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            xml = r.read().decode()
        ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", xml)
        return ids[0] if ids else aid
    except Exception:
        return aid

def strip_comments(text):
    """Remove % comments outside verbatim-like envs; keep \\% escapes."""
    out = []
    i, n = 0, len(text)
    env_stack = []
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n and text[i+1] == "%":
            out.append("\\%")
            i += 2
            continue
        m = re.match(r"\\begin\{([a-zA-Z*]+)\}", text[i:])
        if m:
            env = m.group(1)
            out.append(m.group(0))
            if env in VERBATIM_ENVS:
                env_stack.append(env)
            elif env == "comment":
                end = text.find("\\end{comment}", i + len(m.group(0)))
                if end == -1:
                    out.append("\n% [UNTERMINATED comment env]")
                    i = n
                    continue
                i = end
                out.append("\\end{comment}")
                continue
            i += len(m.group(0))
            continue
        m = re.match(r"\\end\{([a-zA-Z*]+)\}", text[i:])
        if m:
            env = m.group(1)
            out.append(m.group(0))
            if env_stack and env_stack[-1] == env:
                env_stack.pop()
            i += len(m.group(0))
            continue
        if c == "%" and not env_stack:
            j = text.find("\n", i)
            if j == -1:
                break
            out.append("\n")
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out)

def flatten(main_path, root):
    seen = set()
    parts = []

    def resolve(path, depth=0):
        path = os.path.normpath(path)
        if path in seen or depth > 12:
            return
        seen.add(path)
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                src = f.read()
        except Exception:
            parts.append(f"\n% UNRESOLVED INPUT: {path}\n")
            return
        pos = 0
        pat = re.compile(r"\\(?:input|include)\{([^}]+)\}")
        for m in pat.finditer(src):
            parts.append(src[pos:m.start()])
            rel = m.group(1).strip()
            if not rel.endswith(".tex"):
                rel += ".tex"
            cand = os.path.join(os.path.dirname(path), rel)
            if not os.path.exists(cand):
                cand2 = os.path.join(root, rel)
                if os.path.exists(cand2):
                    cand = cand2
            parts.append(f"\n% === begin input {{{m.group(1)}}} ===\n")
            if os.path.exists(cand):
                resolve(cand, depth + 1)
            else:
                parts.append(f"% UNRESOLVED INPUT: {m.group(1)}\n")
            parts.append(f"% === end input {{{m.group(1)}}} ===\n")
            pos = m.end()
        parts.append(src[pos:])

    resolve(main_path)
    return "".join(parts)

def find_main(root):
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".tex"):
                p = os.path.join(dirpath, f)
                try:
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        head = fh.read(3000)
                    if "\\documentclass" in head:
                        return p
                except Exception:
                    pass
    return None

def main():
    root, aid = sys.argv[1], sys.argv[2]
    out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else f"{aid}.tex"
    main_tex = find_main(root)
    if not main_tex:
        sys.exit("no main tex found")
    ver = latest_version(aid)
    flat = flatten(main_tex, root)
    clean = strip_comments(flat)
    header = (f"% ============================================================\n"
              f"% arXiv {aid} (latest: {ver}) — flattened LaTeX source\n"
              f"% flattened+comment-stripped by research-assistant texflatten.py\n"
              f"% main: {os.path.relpath(main_tex, root)} | fetched: {datetime.date.today().isoformat()}\n"
              f"% ============================================================\n")
    with open(out, "w", encoding="utf-8") as f:
        f.write(header + clean)
    print(f"{aid}: latest={ver} | flatten {len(flat)//1024}KB -> strip -> {len(clean)//1024}KB -> {out}")

if __name__ == "__main__":
    main()
