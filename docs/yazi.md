# Yazi

Yazi is the terminal file manager used here. Install the latest stable official release; do not use Flatpak or Snap.

## Install

Use the archive matching the platform:

- Fedora x86_64: `yazi-x86_64-unknown-linux-gnu.zip`
- Intel macOS: `yazi-x86_64-apple-darwin.zip`
- Apple Silicon macOS: `yazi-aarch64-apple-darwin.zip`

After unpacking the archive:

```sh
mkdir -p ~/.local/bin
cp yazi-*/yazi yazi-*/ya ~/.local/bin/
chmod +x ~/.local/bin/yazi ~/.local/bin/ya
```

The current installed version is `26.9.1`. Bash completions from the archive go in `~/.local/share/bash-completion/completions/`.

## Configure

Copy the repository configuration and install the declared packages:

```sh
mkdir -p ~/.config/yazi
cp -a .config/yazi/. ~/.config/yazi/
cd ~/.config/yazi && ya pkg install
```

The configuration contains the `vscode-light-modern` flavor, light/dark theme settings, and `o`/`O` keybindings for opening files in the editor (using a new tmux window when running inside tmux).
