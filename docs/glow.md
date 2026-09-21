# Glow

[Glow](https://github.com/charmbracelet/glow) renders Markdown in a terminal.
The tracked configuration is `.config/glow/glow.yml`; its installed location is
`~/.config/glow/glow.yml`.

## Install

On this Linux host, install the official prebuilt release in the user-local
binary directory:

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

Deploy the tracked configuration:

```sh
mkdir -p ~/.config/glow
cp -p ~/dotfiles/.config/glow/glow.yml ~/.config/glow/
```

The current configuration uses the light style, enables pager mode, disables
line wrapping, and renders only consecutive newlines as line breaks with
`preserveNewLines: false`. Render a file with:

```sh
glow README.md
```

Verify the installed copy matches the repository copy:

```sh
cmp -s ~/dotfiles/.config/glow/glow.yml ~/.config/glow/glow.yml && \
  echo 'Glow configuration copies match.'
```

## Refresh the tracked copy

After changing the live configuration, refresh the repository copy:

```sh
mkdir -p ~/dotfiles/.config/glow
cp -p ~/.config/glow/glow.yml ~/dotfiles/.config/glow/
```

## Remove

Remove the user-local Linux installation with:

```sh
rm ~/.local/bin/glow
```

On macOS, use `brew uninstall glow`.
