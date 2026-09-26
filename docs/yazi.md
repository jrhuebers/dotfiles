# Yazi

Yazi is the terminal file manager used here. Install the latest stable official release; do not use Flatpak or Snap.

## Dependency: `pdftoppm`

Yazi's PDF preview/open workflow requires `pdftoppm`, provided by Poppler.
Install it on every machine before configuring Yazi:

Ubuntu/Debian:

```sh
sudo apt update
sudo apt install poppler-utils
```

Fedora/RHEL:

```sh
sudo dnf install poppler-utils
```

macOS with Homebrew:

```sh
brew install poppler
```

Verify the dependency with:

```sh
command -v pdftoppm
pdftoppm -v
```

On this Ubuntu host, where `sudo` is unavailable, `pdftoppm` is installed
user-locally at `~/.local/bin/pdftoppm`; its extracted Poppler runtime is under
`~/.local/opt/poppler-utils-24.02.0-1ubuntu9.9/`.

## Install

Use the archive matching the platform:

- Linux x86_64 (glibc, including Ubuntu/Fedora): `yazi-x86_64-unknown-linux-gnu.zip`
- Intel macOS: `yazi-x86_64-apple-darwin.zip`
- Apple Silicon macOS: `yazi-aarch64-apple-darwin.zip`

Verify the downloaded archive against the SHA-256 digest published for the selected GitHub release before unpacking it.

After unpacking the archive:

```sh
mkdir -p ~/.local/bin
cp yazi-*/yazi yazi-*/ya ~/.local/bin/
chmod +x ~/.local/bin/yazi ~/.local/bin/ya
```

The current installed version is `26.9.1`; the RCP cluster installation was verified on 2026-09-22. Bash completions from the archive go in `~/.local/share/bash-completion/completions/`.

## Configure

The repository is the source of truth for Yazi configuration. Local configuration files under `~/.config/yazi/` should be symlinks to the corresponding tracked files under `~/dotfiles/.config/yazi/`; do not copy these files. Generated package content, such as installed flavors, remains local.

Symlink the repository configuration and install the declared packages:

```sh
mkdir -p ~/.config/yazi
for file in keymap.toml package.toml theme.toml yazi.toml; do
  ln -sfn ~/dotfiles/.config/yazi/$file ~/.config/yazi/$file
done
cd ~/.config/yazi && ya pkg install
```

The repository also provides `cd-quit.yazi`, a synchronous local plugin that makes Enter on a hovered directory save its path to a separate temporary selection file and quit Yazi without first loading that directory. The wrapper changes into that selected directory after Yazi exits. This avoids the fleeting unfinished-tasks prompt caused by quitting while Yazi is still processing a `cd` action. If Yazi is launched without the wrapper, Enter navigates into the directory normally. Deploy the plugin and shell wrapper alongside the tracked configuration:

```sh
mkdir -p ~/.config/yazi/plugins
ln -sfn ~/dotfiles/.config/yazi/plugins/cd-quit.yazi ~/.config/yazi/plugins/cd-quit.yazi
ln -sfn ~/dotfiles/.config/yazi/shell-wrapper.sh ~/.config/yazi/shell-wrapper.sh
```

The tracked Bash profile sources `~/.config/yazi/shell-wrapper.sh`; if the profile is installed manually, retain this line in `~/.bashrc`:

```sh
[ -r "$HOME/.config/yazi/shell-wrapper.sh" ] && . "$HOME/.config/yazi/shell-wrapper.sh"
```

Use `y` rather than `yazi` to launch Yazi: **calling `yazi` directly does not change the parent shell**, and the plugin deliberately treats Enter on directories as ordinary navigation when the wrapper is absent. The Bash wrapper passes `--cwd-file` to Yazi for normal quits and gives the plugin a separate per-invocation selection file for Enter; the selected path takes precedence when present. The wrapper reads the whole path even when `read -d ''` returns nonzero because Yazi does not terminate paths with NUL. Enter on a directory quits Yazi into that directory; pressing `q` still quits into Yazi's current directory, while `Q` intentionally suppresses the directory change. For another shell, install and source an equivalent wrapper in that shell's startup profile; sourcing the Bash profile is not a substitute.

Verify in a new interactive Bash session (or after `source ~/.bashrc`):

```sh
type y
y
# Hover over a directory and press Enter; Yazi should close.
pwd
```

The directory reported by `pwd` should be the hovered directory. If Enter only opens the directory in Yazi, check that `type y` reports a function and that you launched with `y`, not `yazi`.

The configuration contains the `vscode-light-modern` flavor, light/dark theme settings, an `e` keybinding that edits the hovered file, and `o`/`O` keybindings that send PDFs to `xdg-open` and open other files in the editor (using a new tmux window when running inside tmux). Pressing Enter on `.md` files uses the standalone `md` viewer; Yazi blocks until the pager exits. Yazi's default open action also sends PDFs to `xdg-open`. The editor is selected through the shell environment:

```sh
export EDITOR=vim
export VISUAL=vim
```

These exports are configured in `~/.bashrc`.

## Remove

For a system installation, remove Poppler with the matching package manager,
for example `sudo apt remove poppler-utils` or `brew uninstall poppler`. For
the user-local installation on this host:

```sh
rm -f ~/.local/bin/pdftoppm
rm -rf ~/.local/opt/poppler-utils-24.02.0-1ubuntu9.9
```
