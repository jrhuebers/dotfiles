#!/usr/bin/env python3
"""Fetch latest arXiv papers into one self-contained directory per paper."""
import argparse
from contextlib import contextmanager
import gzip
import http.client
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from assets import copy_assets
from download import MAX_BYTES, UA, request
from flatten_tex import flatten
from qa_corpus import check_paper

ID = re.compile(r"\d{4}\.\d{4,5}$")
ATOM = "{http://www.w3.org/2005/Atom}"
@contextmanager
def fetching_stage(aid: str, stage: str):
    """Keep CLI failures attributable to a paper and pipeline stage."""
    try:
        yield
    except Exception as exc:
        raise RuntimeError(f"{stage} failed for {aid}: {exc}") from exc


class AbsMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values: dict[str, list[str]] = {}

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            fields = dict(attrs)
            if fields.get("name") in ("citation_title", "citation_author", "citation_abstract"):
                self.values.setdefault(fields["name"], []).append(fields.get("content", ""))


def metadata(aid: str) -> tuple[str, str, list[str], str]:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid, "max_results": 1})
    try:
        feed = ET.fromstring(request(url))
        entry = feed.find(f"{ATOM}entry")
        if entry is None:
            raise ValueError(f"arXiv ID not found: {aid}")
        version = entry.findtext(f"{ATOM}id", "").rsplit("/", 1)[-1]
        title = " ".join(entry.findtext(f"{ATOM}title", "").split())
        authors = [" ".join(a.findtext(f"{ATOM}name", "").split()) for a in entry.findall(f"{ATOM}author")]
        abstract = " ".join(entry.findtext(f"{ATOM}summary", "").split())
    except (urllib.error.URLError, OSError, EOFError, http.client.IncompleteRead, ET.ParseError) as exc:
        if isinstance(exc, urllib.error.HTTPError) and exc.code not in (406, 408, 429, 500, 502, 503, 504):
            raise
        html = request(f"https://arxiv.org/abs/{aid}").decode("utf-8", errors="replace")
        parser = AbsMetadata()
        parser.feed(html)
        versions = [int(v) for v in re.findall(rf"arxiv\.org/abs/{re.escape(aid)}v(\d+)", html)]
        version = f"{aid}v{max(versions)}" if versions else ""
        title = " ".join(parser.values.get("citation_title", [""])[0].split())
        authors = parser.values.get("citation_author", [])
        abstract = " ".join(parser.values.get("citation_abstract", [""])[0].split())
    if not re.fullmatch(re.escape(aid) + r"v\d+", version) or not title or not authors:
        raise ValueError(f"missing or inconsistent arXiv metadata for {aid}")
    return version, title, authors, abstract


def extract_source(data: bytes, root: Path) -> str:
    """Extract only regular, bounded tar members; reject links and traversals."""
    root.mkdir()
    if data.startswith(b"\x1f\x8b"):
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                total = 0
                for member in tf.getmembers():
                    name = PurePosixPath(member.name)
                    if (name.is_absolute() or ".." in name.parts or not member.name or
                            not (member.isdir() or member.isfile())):
                        raise ValueError(f"unsafe source member: {member.name}")
                    if member.isfile():
                        total += member.size
                        if total > MAX_BYTES or member.size > MAX_BYTES:
                            raise ValueError("source archive too large")
                        destination = root.joinpath(*name.parts)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with tf.extractfile(member) as source, destination.open("wb") as output:
                            output.write(source.read())
                return "tar.gz"
        except tarfile.ReadError:
            text = gzip.decompress(data)
            if len(text) > MAX_BYTES or b"\\documentclass" not in text:
                raise ValueError("gzip source is not LaTeX")
            (root / "main.tex").write_bytes(text)
            return "tex.gz"
    if b"\\documentclass" in data[:200_000]:
        (root / "main.tex").write_bytes(data)
        return "tex"
    raise ValueError("arXiv source is neither tar.gz nor LaTeX (PDF/PS or error page?)")


def fetch_one(outdir: Path, aid: str, *, prune_macros: str = "safe") -> None:
    if not ID.fullmatch(aid):
        raise ValueError(f"invalid bare modern arXiv ID: {aid}")
    outdir.mkdir(parents=True, exist_ok=True)
    paper_dir = outdir / aid
    if paper_dir.exists():
        raise FileExistsError(f"paper directory already exists for {aid}; use a new directory to refresh it")
    with fetching_stage(aid, "metadata"):
        version, title, authors, abstract = metadata(aid)
    author_text = "; ".join(authors) if isinstance(authors, list) else str(authors).replace(", ", "; ")
    print(f"{aid}: {version}: {title} — {author_text}", flush=True)
    with fetching_stage(aid, "PDF download"):
        pdf = request(f"https://arxiv.org/pdf/{aid}")
        if not pdf.startswith(b"%PDF-"):
            raise ValueError("PDF endpoint did not return a PDF")
    with fetching_stage(aid, "source download"):
        try:
            source = request(f"https://arxiv.org/e-print/{aid}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            source = b""
    if not source or source.startswith((b"%PDF-", b"%!PS")):
        paper_dir.mkdir(parents=True)
        (paper_dir / f"{aid}.pdf").write_bytes(pdf)
        (paper_dir / "metadata.json").write_text(json.dumps({"arxiv_id": aid, "version": version, "title": title, "authors": authors, "abstract": abstract}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (paper_dir / "source-unavailable.txt").write_text(
            f"arXiv {version} | source unavailable (404/PDF/PS); PDF only\n", encoding="utf-8")
        print(f"{aid}: PDF-only; author LaTeX source unavailable", flush=True)
        return
    with tempfile.TemporaryDirectory(prefix=".paper-fetch-", dir=outdir) as tmp:
        stage = Path(tmp) / aid
        stage.mkdir(parents=True, exist_ok=True)
        extracted = stage / "extracted"
        with fetching_stage(aid, "source extraction"):
            kind = extract_source(source, extracted)
        (stage / f"{aid}.pdf").write_bytes(pdf)
        # Keep a standalone plain-TeX source distinct from the flattened output.
        # The compressed single-file form already has a distinct .tex.gz suffix.
        original_name = f"{aid}.tar.gz" if kind == "tar.gz" else (f"{aid}.source.tex" if kind == "tex" else f"{aid}.{kind}")
        (stage / original_name).write_bytes(source)
        with fetching_stage(aid, "asset materialization"):
            asset_map = copy_assets(extracted, stage)
        with fetching_stage(aid, "TeX flattening/asset remapping"):
            flatten(extracted, aid, version, stage / f"{aid}.tex", prune_macros=prune_macros, asset_map=asset_map)
        (stage / "metadata.json").write_text(json.dumps({"arxiv_id": aid, "version": version, "title": title, "authors": authors, "abstract": abstract}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        shutil.rmtree(extracted)
        with fetching_stage(aid, "corpus QA"):
            errors = check_paper(stage, aid, version=version)
            if errors:
                raise ValueError("; ".join(errors))
        with fetching_stage(aid, "publication"):
            stage.replace(paper_dir)
    print(f"{aid}: PDF, flattened TeX, source archive, figures and bibliography saved in {paper_dir}", flush=True)


def paper_dirs(outdir: Path) -> list[Path]:
    return sorted(path for path in outdir.iterdir() if path.is_dir() and any(path.glob("*.pdf"))) if outdir.exists() else []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outdir", type=Path)
    parser.add_argument("ids", nargs="+")
    parser.add_argument("--prune-macros", choices=("safe", "off"), default="safe",
                        help="final single-file macro cleanup (default: safe)")
    args = parser.parse_args()
    failed = False
    for aid in args.ids:
        try:
            fetch_one(args.outdir, aid, prune_macros=args.prune_macros)
        except Exception as exc:
            print(f"{aid}: ERROR: {exc}", flush=True)
            failed = True
    for paper_dir in paper_dirs(args.outdir):
        aid = paper_dir.name
        errors = check_paper(paper_dir, aid)
        print(f"{aid}: {'FAIL: ' + '; '.join(errors) if errors else 'corpus QA OK'}")
        failed |= bool(errors)
    if not failed and paper_dirs(args.outdir):
        scripts = Path(__file__).parent
        for script, phase in (("figindex.py", "figure indexing"), ("refindex.py", "reference indexing"), ("index.py", "metadata indexing")):
            try:
                with fetching_stage(str(args.outdir), phase):
                    subprocess.run([sys.executable, str(scripts / script), str(args.outdir)], check=True)
            except RuntimeError as exc:
                print(f"ERROR: {exc}", flush=True)
                failed = True
                break
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
