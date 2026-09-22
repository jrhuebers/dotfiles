# Glow

[Glow](https://github.com/charmbracelet/glow) renders Markdown in a terminal.
The canonical configuration is `.config/glow/glow.yml`; on each machine,
`~/.config/glow/glow.yml` must be a symlink to that tracked file.

## Install

On supported profiles, install the official prebuilt release in the user-local
binary directory. The current Linux x86_64 cluster installation instead uses
an unreleased upstream `main` build at commit `6b365ee` because it contains the
TUI direct-file rendering fix. Stable installations should use the official
release instructions below.

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
