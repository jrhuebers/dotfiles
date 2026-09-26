"""Offline failure/edge-case checks; live arXiv test uses the CLI."""
import gzip
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_papers import extract_source, fetch_one
from flatten_tex import find_main, flatten, strip_comments
from qa_corpus import check_paper


class PipelineTests(unittest.TestCase):
    def test_comments(self):
        text = "a% drop\n\\% keep\n\\\\% drop\n\\begin{verbatim}\nraw%keep\n\\end{verbatim}\nb%drop"
        self.assertEqual(strip_comments(text), "a\n\\% keep\n\\\\\n\\begin{verbatim}\nraw%keep\n\\end{verbatim}\nb")

    def test_main_largest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "stub.tex").write_text(r"\documentclass{article}\input{real}")
            (root / "real.tex").write_text(r"\documentclass{article}" + "x" * 100)
            self.assertEqual(find_main(root).name, "real.tex")

    def test_flatten_multifile(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sections").mkdir()
            (root / "main.tex").write_text("\\documentclass{article}\n\\begin{document}\n\\input{sections/body}\n\\end{document}\n")
            (root / "sections/body.tex").write_text("Included section " + "words " * 60 + "% discard\n\\% kept\n\\begin{verbatim}\nraw%keep\n\\end{verbatim}\n")
            out = root / "flat.tex"
            flatten(root, "1706.03762", "1706.03762v7", out)
            text = out.read_text()
            self.assertIn("Included section", text)
            self.assertNotIn("discard", text)
            self.assertIn(r"\% kept", text)
            self.assertIn("raw%keep", text)
            self.assertNotIn(r"\input{sections/body}", text)
            self.assertFalse(check_paper(root, "1706.03762") == [])  # PDF and source intentionally absent

    def test_unsafe_tar(self):
        for name in ("../outside.tex", "/tmp/outside.tex", "./safe/../../outside.tex"):
            with tempfile.TemporaryDirectory() as d:
                archive = io.BytesIO()
                with tarfile.open(fileobj=archive, mode="w:gz") as tf:
                    data = b"evil"
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    tf.addfile(info, io.BytesIO(data))
                with self.assertRaises(ValueError):
                    extract_source(archive.getvalue(), Path(d) / "src")

    def test_single_file_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "source"
            data = b"\\documentclass{article}\n\\begin{document}hi\\end{document}\n"
            self.assertEqual(extract_source(gzip.compress(data), root), "tex.gz")
            self.assertEqual((root / "main.tex").read_bytes(), data)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "source"
            self.assertEqual(extract_source(data, root), "tex")
            self.assertEqual((root / "main.tex").read_bytes(), data)

    def test_pdf_only_on_missing_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            error = urllib.error.HTTPError("https://arxiv.org/e-print/1706.03762", 404, "Not Found", {}, None)
            with patch("fetch_papers.metadata", return_value=("1706.03762v7", "Title", "Author")):
                with patch("fetch_papers.request", side_effect=[b"%PDF-" + b"x" * 12000, error]):
                    fetch_one(root, "1706.03762")
            self.assertEqual(check_paper(root, "1706.03762", "1706.03762v7"), [])
            self.assertFalse((root / "arxiv_1706.03762.tex").exists())
            (root / "arxiv_1706.03762.source-unavailable.txt").write_text("arXiv 1706.03762v1 | source unavailable\n")
            self.assertTrue(check_paper(root, "1706.03762", "1706.03762v7"))

    def test_bad_id_and_missing_qa(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                fetch_one(Path(d), "1706.03762v1")
            self.assertTrue(check_paper(Path(d), "1706.03762"))


if __name__ == "__main__":
    unittest.main()
