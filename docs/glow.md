# Glow

[Glow](https://github.com/charmbracelet/glow) renders Markdown in a terminal.
The canonical configuration is `.config/glow/glow.yml`; on each machine,
`~/.config/glow/glow.yml` must be a symlink to that tracked file.

## Install

On supported profiles, install the official prebuilt release in the user-local
binary directory. The Linux x86_64 installation on the RCP cluster was verified
with Glow 3.0.0 on 2026-09-22:

```sh
mkdir -p ~/.local/bin
# Download the Linux x86_64 tarball for the desired Glow release, then:
tar -xzf glow_*_Linux_x86_64.tar.gz
install -m 0755 glow ~/.local/bin/glow
```

Ensure `~/.local/bin` is in `PATH`, then verify the install:

```sh
glow --version
```

On macOS, Homebrew provides Glow:

```sh
brew install glow
```

## Configuration

Deploy the tracked configuration as a symlink:

```sh
mkdir -p ~/.config/glow
# Back up an existing regular file or symlink before replacing it.
if [ -e ~/.config/glow/glow.yml ] || [ -L ~/.config/glow/glow.yml ]; then
  mv ~/.config/glow/glow.yml ~/.config/glow/glow.yml.backup-$(date +%Y%m%d-%H%M%S)
fi
ln -s ~/dotfiles/.config/glow/glow.yml ~/.config/glow/glow.yml
```

The current configuration uses the light style, enables pager mode, disables
line wrapping, and renders only consecutive newlines as line breaks with
`preserveNewLines: false`. Render a file with:

```sh
glow README.md
```

Verify the installed copy matches the repository copy:

```sh
test "$(readlink -f ~/.config/glow/glow.yml)" = \
  "$(readlink -f ~/dotfiles/.config/glow/glow.yml)" && \
  echo 'Glow configuration symlink is correct.'
```

## Change the configuration

Edit the tracked source directly, then commit and push it. All machine-local
paths should remain symlinks to this source:

```sh
${EDITOR:-vi} ~/dotfiles/.config/glow/glow.yml
```

## Remove

Remove the user-local Linux installation with:

```sh
rm ~/.local/bin/glow
```

On macOS, use `brew uninstall glow`.
