# latexpand

`latexpand` is required on the Cluster profile because the paper-fetching skill uses it to inline LaTeX `\input` and `\include` files before reading papers.

## Cluster installation

Install it in the user-local TeX Live installation; do not use `sudo` or install a system-wide package on a shared cluster host.

```sh
export PATH="$HOME/.local/texlive/2026/bin/x86_64-linux:$PATH"
tlmgr install latexpand
hash -r
```

If TeX Live is not installed, follow the user-local TeX Live procedure in `~/admin-docs/pandoc-tectonic-texlive.md` first, then run the commands above. Adjust the TeX Live year and binary directory to the installed release and architecture.

## Verify

```sh
command -v latexpand
latexpand --version
tlmgr info --only-installed latexpand
```

The expected current version on this cluster is `latexpand version v1.7.2`; the executable is under `~/.local/texlive/2026/bin/x86_64-linux/`.

## Pipeline use

Run the paper-fetching command rather than invoking `latexpand` manually; its `flatten_tex.py` wrapper runs `latexpand --keep-comments`, removes comments safely, preserves code blocks, collapses excessive blank lines, and adds provenance.

## Removal

Remove only the TeX Live package when no configured workflow needs it:

```sh
tlmgr remove latexpand
```
