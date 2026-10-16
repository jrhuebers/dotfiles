---
name: paper-fetching
description: "Manage an arXiv paper library with the standalone arxiv-papers CLI: fetching, tags, metadata, filtering, validation, and generated indexes."
---

# arXiv paper library

Use the single public command `arxiv-papers`, implemented in https://github.com/jrhuebers/arxiv-papers and locally at `/nfs_home/huebers/arxiv-papers`. The scripts retained in this skill directory are legacy implementation files; do not use them for the new library workflow.

The default library is `./arxiv-papers/`, relative to the current working directory. Use `--library /path/to/library` explicitly when working across directories. Python 3.10+ and Perl on PATH are required for processing LaTeX source. The CLI always uses its bundled, pinned latexpand v1.7.2; no separate latexpand or TeX Live installation is needed. Read the repository README or `arxiv-papers --help` for the full interface.

```bash
arxiv-papers --library /path/to/library add 1706.03762 --tag reading
arxiv-papers --library /path/to/library list --tag reading --json
arxiv-papers --library /path/to/library list --tag GNNs --tag datasets --match all --json
arxiv-papers --library /path/to/library list --untagged --json
arxiv-papers --library /path/to/library list --author Miolane --title "synthetic graph" --json
arxiv-papers --library /path/to/library list --content "inductive generalization" --json
arxiv-papers --library /path/to/library metadata 1706.03762 --json
arxiv-papers --library /path/to/library tag add 1706.03762 --tag transformers
arxiv-papers --library /path/to/library tag remove 1706.03762 --tag reading
arxiv-papers --library /path/to/library update 1706.03762
arxiv-papers --library /path/to/library check --json
arxiv-papers --library /path/to/library rebuild-indexes
```

Use CLI listing for tag subdivisions instead of maintaining tag-specific Markdown files. All text filters ignore case and accents. Title/abstract/content require every query word in any order; phrase flags require consecutive words. Author matching is substring-based. Tags match exactly and combine with OR unless `--match all` is given; different fields combine with AND. Optional `--fuzzy` applies only to title/author matching. Content search uses best-effort prose extracted from flattened TeX; PDF-only papers have no searchable content.

One revision per paper is installed. Bare IDs resolve to the installed version for metadata/tag/remove; explicit versions must match exactly. `add` skips installed papers and never replaces them; `update` explicitly replaces a revision, preserving tags. Both accept pinned versions and old-style IDs such as `hep-th/9901001v3`. Directory names include the revision and encode old-style slashes as underscores.

Each paper has `metadata.json` with `arxiv_id`, `version` (`vN`), title, author list, abstract, tags, first submission date, and downloaded-version submission date. Metadata may be edited directly, then `rebuild-indexes` regenerates derived files. `abstract.md` contains the per-paper abstract. `INDEX.md` lists titles, versioned IDs, and authors only. Do not manually edit downloaded PDFs, sources, flattened TeX, materialized assets, or generated indexes/abstracts.

`arxiv-papers remove ID ...` permanently deletes papers; use only when deletion is explicitly requested. There is no migration command for old corpora. Use a new library directory rather than running the new CLI on an existing legacy corpus.

`--json` gives structured stdout; download diagnostics go to stderr. Any batch fetch/update failure returns nonzero while leaving successful papers intact. Offline tests are in the standalone repository: `python3 -m unittest discover -s tests -v` after installation.
