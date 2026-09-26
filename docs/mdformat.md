# mdformat

`mdformat` is the upstream Python Markdown formatter. The cluster installation is user-local at `~/.local/bin/mdformat` and is installed with `uv tool install mdformat`.

The Bash alias `mdclean` runs `mdformat --wrap no`, which keeps prose blocks on one physical line. Reload Bash or start a new shell after deploying the tracked `~/dotfiles/.bashrc`.

For pre-commit, use the upstream hook with a pinned release:

```yaml
repos:
  - repo: https://github.com/hukkin/mdformat
    rev: 1.0.0
    hooks:
      - id: mdformat
        args: [--wrap, no]
```

Verify the installation with `mdformat --version` and the alias with `bash -ic 'alias mdclean'`.
