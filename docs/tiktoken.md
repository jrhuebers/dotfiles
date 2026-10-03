# Token counter CLI

`token-counter-cli` is the required tiktoken-based token counter. It is
published on PyPI and maintained at
https://github.com/puya/token-counter-cli. Install it user-local on every
supported machine; no system-wide package or service is required. The package
installs the `token-counter` command and its isolated `tiktoken` dependency.

## Install or upgrade

Use `uv` so the tool and its Python dependencies remain isolated from the
system Python and other user projects:

```sh
uv tool install --upgrade token-counter-cli
```

The launcher is installed under `~/.local/bin/token-counter`; keep that
directory in `PATH`. `uv` manages the isolated environment under
`~/.local/share/uv/tools/token-counter-cli/`.

## Use

Count a supported text file using the default `cl100k_base` encoding:

```sh
token-counter input.txt
```

Count a LaTeX file by adding its extension explicitly:

```sh
token-counter --extension .tex paper.tex
```

Select an encoding, read standard input, or compare against context limits:

```sh
echo -n "Hello, world!" | token-counter
token-counter --model cl100k_base input.txt
token-counter --check-limits input.txt
```

Use `token-counter --help` for all options. The original `tiktoken` command,
which emits token IDs rather than a count, is not required for normal counting.

## Verify

```sh
command -v token-counter
token-counter --version
token-counter --help
```

Version `0.1.6` and its `tiktoken 0.14.0` dependency were verified on the
current Ubuntu 24.04 cluster host.

## Remove

```sh
uv tool uninstall token-counter-cli
```
