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
