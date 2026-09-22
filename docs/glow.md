# Glow

[Glow](https://github.com/charmbracelet/glow) renders Markdown in a terminal.
The canonical configuration is `.config/glow/glow.yml`; on each machine,
`~/.config/glow/glow.yml` must be a symlink to that tracked file.

## Install

Install a tagged release in the user-local binary directory when one newer
than 3.0.0 is available. Until then, use the pinned upstream commit
`6b365eea95f7541d4af441d971010b09f6082a0e`, which contains the TUI direct-file
rendering fix missing from Glow 3.0.0.

For an official release newer than 3.0.0, download the Linux x86_64 tarball
and install it with:

```sh
mkdir -p ~/.local/bin
# Download the Linux x86_64 tarball for the desired Glow release, then:
tar -xzf glow_*_Linux_x86_64.tar.gz
install -m 0755 glow ~/.local/bin/glow
```

To build the pinned commit from source, use Go 1.26.6 or newer:

```sh
set -eu
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git clone https://github.com/charmbracelet/glow.git "$work/glow"
cd "$work/glow"
git checkout --detach 6b365eea95f7541d4af441d971010b09f6082a0e
go build -trimpath -ldflags "-s -w -X main.Version=main -X main.CommitSHA=$(git rev-parse HEAD)" -o "$work/glow-bin" .
mkdir -p ~/.local/bin
install -m 0755 "$work/glow-bin" ~/.local/bin/glow
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

The current configuration uses the light style, launches Glow in TUI mode,
and disables pager mode. Its width is left at Glow's terminal-size default.
With `preserveNewLines: false`, single newlines are reflowed while blank-line
paragraph breaks remain. Render a file with:

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
