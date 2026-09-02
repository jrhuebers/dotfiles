# Machine setup inventory

This file records the software and personal settings needed to recreate this machine. When setting up a new Linux or macOS computer, clone this repository and use this file as the setup checklist.

## Yazi

Yazi is installed from the latest stable official GitHub release, not Flatpak or Snap. On Fedora x86_64, use `yazi-x86_64-unknown-linux-gnu.zip`; on macOS use the matching `aarch64-apple-darwin` or `x86_64-apple-darwin` archive. Copy `yazi` and `ya` to `~/.local/bin` and make them executable. The current installed version is `26.9.1`.

Install the configuration and its packages from the repository with:

```sh
mkdir -p ~/.config/yazi
cp -a .config/yazi/. ~/.config/yazi/
cd ~/.config/yazi && ya pkg install
```

This installs the `vscode-light-modern` flavor declared in `package.toml`. The configuration includes `keymap.toml`, `theme.toml`, and custom `o`/`O` editor keybindings. Bash completions are installed under `~/.local/share/bash-completion/completions/`.

