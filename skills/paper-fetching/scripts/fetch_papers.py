#!/usr/bin/env python3
"""Fetch latest arXiv papers, verify the complete corpus, and index figures."""
import argparse
import gzip
from html.parser import HTMLParser
import io
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from flatten_tex import flatten
from qa_corpus import check_paper

UA = "paper-fetching/0.1 (research corpus; contact: https://github.com/jrhuebers/dotfiles)"
ID = re.compile(r"\d{4}\.\d{4,5}$")
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_BYTES = 100_000_000
_last_request = 0.0


def request(url: str) -> bytes:
    global _last_request
    delay = 3.2 - (time.monotonic() - _last_request)
    if _last_request and delay > 0:
        time.sleep(delay)
    _last_request = time.monotonic()
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"download exceeds {MAX_BYTES} bytes: {url}")
    return data


class AbsMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values: dict[str, list[str]] = {}

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            fields = dict(attrs)
            if fields.get("name") in ("citation_title", "citation_author"):
                self.values.setdefault(fields["name"], []).append(fields.get("content", ""))


def metadata(aid: str) -> tuple[str, str, str]:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid, "max_results": 1})
    try:
        feed = ET.fromstring(request(url))
        entry = feed.find(f"{ATOM}entry")
        if entry is None:
            raise ValueError(f"arXiv ID not found: {aid}")
        version = entry.findtext(f"{ATOM}id", "").rsplit("/", 1)[-1]
        title = " ".join(entry.findtext(f"{ATOM}title", "").split())
        authors = ", ".join(" ".join(a.findtext(f"{ATOM}name", "").split()) for a in entry.findall(f"{ATOM}author"))
    except urllib.error.HTTPError as exc:
        if exc.code not in (406, 429, 502, 503):
            raise
        # arXiv's API occasionally returns 406 for particular valid IDs.
        html = request(f"https://arxiv.org/abs/{aid}").decode("utf-8", errors="replace")
        parser = AbsMetadata()
        parser.feed(html)
        versions = [int(v) for v in re.findall(rf"arxiv\.org/abs/{re.escape(aid)}v(\d+)", html)]
        version = f"{aid}v{max(versions)}" if versions else ""
        title = " ".join(parser.values.get("citation_title", [""])[0].split())
        authors = ", ".join(parser.values.get("citation_author", []))
    if not re.fullmatch(re.escape(aid) + r"v\d+", version) or not title or not authors:
        raise ValueError(f"missing or inconsistent arXiv metadata for {aid}")
    return version, title, authors


def extract_source(data: bytes, root: Path) -> str:
    """Only regular, bounded tar members; never links, device nodes or traversals."""
    root.mkdir()
    if data.startswith(b"\x1f\x8b"):
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                members = tf.getmembers()
                total = 0
                for m in members:
                    name = PurePosixPath(m.name)
                    if (name.is_absolute() or ".." in name.parts or not m.name or
                            not (m.isdir() or m.isfile())):
                        raise ValueError(f"unsafe source member: {m.name}")
                    if m.isfile():
                        total += m.size
                        if total > MAX_BYTES or m.size > MAX_BYTES:
                            raise ValueError("source archive too large")
                        dest = root.joinpath(*name.parts)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        with tf.extractfile(m) as src, dest.open("wb") as out:
                            out.write(src.read())
                return "tar.gz"
        except tarfile.ReadError:
            # A single gzip-compressed .tex rather than a tar archive.
            text = gzip.decompress(data)
            if len(text) > MAX_BYTES or b"\\documentclass" not in text:
                raise ValueError("gzip source is not LaTeX")
            (root / "main.tex").write_bytes(text)
            return "tex.gz"
    if b"\\documentclass" in data[:200_000]:
        (root / "main.tex").write_bytes(data)
        return "tex"
    raise ValueError("arXiv source is neither tar.gz nor LaTeX (PDF/PS or error page?)")


def fetch_one(outdir: Path, aid: str) -> None:
    if not ID.fullmatch(aid):
        raise ValueError(f"invalid bare modern arXiv ID: {aid}")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "src").mkdir(exist_ok=True)
    pdf_path = outdir / f"arxiv_{aid}.pdf"
    tex_path = outdir / f"arxiv_{aid}.tex"
    src_path = outdir / "src" / f"{aid}.tar.gz"
    if any(p.exists() for p in (pdf_path, tex_path, src_path, outdir / f"arxiv_{aid}.source-unavailable.txt")):
        raise FileExistsError(f"artifacts already exist for {aid}; use a new directory to fetch the latest version")
    version, title, authors = metadata(aid)
    print(f"{aid}: {version}: {title} — {authors}", flush=True)
    pdf = request(f"https://arxiv.org/pdf/{aid}")
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("PDF endpoint did not return a PDF")
    try:
        source = request(f"https://arxiv.org/e-print/{aid}")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        source = b""
    if not source or source.startswith((b"%PDF-", b"%!PS")):
        # No author LaTeX source: retain the PDF, mark the absence explicitly.
        pdf_path.write_bytes(pdf)
        (outdir / f"arxiv_{aid}.source-unavailable.txt").write_text(
            f"arXiv {version} | source unavailable (404/PDF/PS); PDF only\n", encoding="utf-8")
        print(f"{aid}: PDF-only; author LaTeX source unavailable", flush=True)
        return
    with tempfile.TemporaryDirectory(prefix=".paper-fetch-", dir=outdir) as tmp:
        stage = Path(tmp)
        (stage / "src").mkdir()
        kind = extract_source(source, stage / "extracted")
        if kind == "tar.gz":
            (stage / "src" / f"{aid}.tar.gz").write_bytes(source)
        else:
            # A canonical original download, not a fabricated tarball.
            (stage / "src" / f"{aid}.{kind}").write_bytes(source)
        (stage / f"arxiv_{aid}.pdf").write_bytes(pdf)
        flatten(stage / "extracted", aid, version, stage / f"arxiv_{aid}.tex")
        errors = check_paper(stage, aid, version=version)
        if errors:
            raise ValueError("QA failed: " + "; ".join(errors))
        for p in (stage / f"arxiv_{aid}.pdf", stage / f"arxiv_{aid}.tex"):
            p.replace(outdir / p.name)
        for p in (stage / "src").iterdir():
            p.replace(outdir / "src" / p.name)
    print(f"{aid}: PDF, flattened TeX and original {kind} saved in {outdir}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("outdir", type=Path)
    p.add_argument("ids", nargs="+")
    args = p.parse_args()
    failed = False
    for aid in args.ids:
        try:
            fetch_one(args.outdir, aid)
        except Exception as exc:
            print(f"{aid}: ERROR: {exc}", flush=True)
            failed = True
    # Check all papers in the destination, not just newly fetched ones.
    aids = {path.stem.removeprefix("arxiv_") for path in args.outdir.glob("arxiv_*.pdf")}
    aids.update(path.stem.removeprefix("arxiv_") for path in args.outdir.glob("arxiv_*.tex"))
    for aid in sorted(aids):
        errors = check_paper(args.outdir, aid)
        print(f"{aid}: {'FAIL: ' + '; '.join(errors) if errors else 'corpus QA OK'}")
        failed |= bool(errors)
    if not failed and any(args.outdir.glob("arxiv_*.tex")):
        # Regenerate one index covering both new and existing TeX papers.
        index_script = Path(__file__).with_name("figindex.py")
        subprocess.run([sys.executable, str(index_script), str(args.outdir)], check=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
