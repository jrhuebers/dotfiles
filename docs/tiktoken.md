# tiktoken CLI

The `tiktoken-cli` package installs the `tiktoken` command and its Python
library on every supported machine where Python is available. It is installed
user-local; no system-wide package or service is required.

## Install or upgrade

On Ubuntu 24.04, whose Python uses the externally-managed-environment policy:

```sh
python3 -m pip install --user --break-system-packages --upgrade tiktoken-cli
```

On a machine whose Python does not enforce that policy, omit
`--break-system-packages`:

```sh
python3 -m pip install --user --upgrade tiktoken-cli
```

On Apple Silicon macOS with Homebrew Python, the interpreter also enforces
PEP 668. Install into the user site without changing Homebrew's site-packages:

```sh
brew install python
/opt/homebrew/bin/python3 -m pip install --user --break-system-packages --upgrade tiktoken-cli
```

The Linux command installs the executable under `~/.local/bin/tiktoken`; keep
`~/.local/bin` in `PATH`. On macOS, add the user script directory to `PATH` if
Homebrew Python does not already expose it:

```sh
export PATH="$HOME/Library/Python/$(/opt/homebrew/bin/python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
```

The `uv` tool manager is also supported and creates an isolated user-local
installation:

```sh
uv tool install --upgrade tiktoken-cli
```

## Use

Encode text and write token IDs to standard output:

```sh
echo -n "Hello, world!" | tiktoken --model gpt-4o - -
```

Count tokens in a file:

```sh
tiktoken --model gpt-4o input.txt - | wc -l
```

Use `tiktoken --help` for the supported model list and input/output syntax.

## Verify

```sh
command -v tiktoken
tiktoken --help
python3 -c 'import tiktoken; print(tiktoken.__version__)'
```

Always verify using the same interpreter used for installation. Reinstall after
changing Python minor versions. Version `0.14.0` was verified on the current
Ubuntu 24.04 cluster host and with Homebrew Python 3.14 on arm64 macOS.

## Remove

For a pip user installation:

```sh
python3 -m pip uninstall tiktoken-cli tiktoken
```

For a `uv` tool installation:

```sh
uv tool uninstall tiktoken-cli
```
