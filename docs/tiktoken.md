# tiktoken

`tiktoken` is installed on every supported machine where Python is available.
It is a user-local Python package; no system-wide package or service is
required.

## Install or upgrade

On Ubuntu 24.04, whose Python uses the externally-managed-environment policy:

```sh
python3 -m pip install --user --break-system-packages --upgrade tiktoken
```

On a machine whose Python does not enforce that policy, omit
`--break-system-packages`:

```sh
python3 -m pip install --user --upgrade tiktoken
```

On Apple Silicon macOS with Homebrew Python, the interpreter also enforces
PEP 668. Install into the user site without changing Homebrew's site-packages:

```sh
brew install python
/opt/homebrew/bin/python3 -m pip install --user --break-system-packages --upgrade tiktoken
/opt/homebrew/bin/python3 -c 'import tiktoken; print(tiktoken.__version__)'
```

The user site is normally under `~/Library/Python/<major.minor>/lib/python/site-packages`.
Always verify using the same interpreter used for installation; Apple's
`/usr/bin/python3` is a separate interpreter. Reinstall after changing Python
minor versions. Version `0.14.0` was verified with Homebrew Python 3.14 on arm64.

The current cluster install is in
`~/.local/lib/python3.12/site-packages/`. The cluster home directory is shared,
so the package is available from other cluster nodes that provide the same
Python 3.12 user site; install it separately on personal machines.

## Verify

```sh
python3 -c 'import tiktoken; e=tiktoken.get_encoding("cl100k_base"); print(tiktoken.__version__, e.encode("hello"))'
```

## Remove

```sh
python3 -m pip uninstall tiktoken regex
```

Only remove `regex` if it is not needed by another user-local package.
