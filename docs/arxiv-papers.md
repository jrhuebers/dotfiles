# arxiv-papers

`arxiv-papers` is the standalone CLI for a filesystem-backed, tagged arXiv paper library. Install the CLI on every supported machine; keep each paper library in a separate research workspace or synchronized storage location.

## Install on every machine

The preferred installation uses the required user-local `uv` tool manager and the public GitHub repository:

```sh
uv tool install --upgrade git+https://github.com/jrhuebers/arxiv-papers.git
```

`uv` places the `arxiv-papers` launcher in its user tool bin directory, normally `~/.local/bin`; ensure that directory is on `PATH`. The package requires Python 3.10+ and Perl. If `uv` cannot find a suitable Python interpreter, install one with `uv python install 3.12` and repeat the tool installation. No separate TeX Live or `latexpand` installation is needed: the package bundles pinned `latexpand` v1.7.2.

For development from the tracked source checkout instead of the published Git repository, use an editable user-local tool installation:

```sh
uv tool install --editable ~/arxiv-papers
```

The repository checkout is source; the installed launcher and isolated environment are managed by `uv`. Do not put a paper library inside the source checkout unless that is intentional.

## Verify

```sh
command -v arxiv-papers
arxiv-papers --version
arxiv-papers --help
command -v perl
```

On a shared cluster home, one user-local installation is visible on compatible login and compute hosts that mount the same home directory. Install separately on machines with a different home filesystem, such as personal workstations, Oracle, or RCP.

## Use

Select the library explicitly when working outside a project directory:

```sh
arxiv-papers --library ~/research/arxiv-papers add 1706.03762 --tag reading
arxiv-papers --library ~/research/arxiv-papers list --tag reading --json
arxiv-papers --library ~/research/arxiv-papers check --json
```

Read the upstream [`README.md`](https://github.com/jrhuebers/arxiv-papers/blob/main/README.md) or run `arxiv-papers --help` for the complete command interface. The CLI downloads papers and therefore needs outbound network access when adding or updating entries.

## Update and remove

```sh
uv tool upgrade arxiv-papers
uv tool uninstall arxiv-papers
```

Removing the CLI does not remove paper libraries. Keep backups of important libraries; there is no migration command for older paper-fetching corpora.
