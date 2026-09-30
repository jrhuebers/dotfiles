# md

`md` is the primary Markdown viewer for this setup. It is maintained in the
standalone public repository:

<https://github.com/jrhuebers/md>

It replaces Glow for everyday Markdown viewing. Glow may remain installed for
reference or comparison, but it is not the configured viewer.

## Install

Clone or update the standalone repository for the canonical configuration:

```sh
git clone https://github.com/jrhuebers/md.git ~/md
```

For Linux x86_64, install the official release archive after verifying its published SHA-256 checksum. The 0.6.40 release below predates the built-in pager terminal-input improvement; if you encounter terminal input problems when using `md` inside another TUI, try building current source (commit `ed52c94` or later) using the next example instead:

```sh
version=0.6.40
archive="md-v${version}-x86_64-unknown-linux-gnu.tar.gz"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
curl -fsSL -o "$work/$archive" "https://github.com/jrhuebers/md/releases/download/v${version}/$archive"
curl -fsSL -o "$work/$archive.sha256" "https://github.com/jrhuebers/md/releases/download/v${version}/$archive.sha256"
test "$(awk '{print $1}' "$work/$archive.sha256")" = "$(sha256sum "$work/$archive" | awk '{print $1}')"
mkdir -p ~/.local/opt/md-${version}
tar -xzf "$work/$archive" --strip-components=1 -C ~/.local/opt/md-${version}
mkdir -p ~/.local/bin ~/.config
ln -sfn ~/.local/opt/md-${version}/bin/md ~/.local/bin/md
ln -sfn ~/md/.config/md.yaml ~/.config/md.yaml
```

Current source requires Cargo and the dependencies pinned in `Cargo.lock`;
the old direct `rustc` command no longer works. On Apple Silicon macOS, build
natively (the published release archive is Linux-only):

```sh
brew install rust
cd ~/md
cargo build --release --locked
mkdir -p ~/.local/bin ~/.config
install -m 0755 target/release/md ~/.local/bin/md
ln -sfn ~/md/.config/md.yaml ~/.config/md.yaml
```

The Node.js math bridge and vendored renderer remain in the checkout. Keep
`~/md` available and Node.js in `PATH` for full math rendering. The same Cargo
build works on supported Linux platforms with Rust installed. To remove this
installation, remove only `~/.local/bin/md` and the `~/.config/md.yaml` symlink.

The viewer uses its built-in interactive pager when `$PAGER` is unset, or the specified external pager when set (for example, `PAGER='less -R' md FILE`). Since `jrhuebers/md` commit `ed52c94`, the built-in pager keeps terminal input blocking to avoid timeouts being mistaken for EOF by another TUI. This is a preventive change, not a confirmed fix for every Yazi input freeze; an external pager remains a workaround if the problem persists. LaTeX-to-Unicode rendering is enabled by default and can be disabled with `render_latex: false` in `~/.config/md.yaml`.

## Verify

```sh
md --version
md README.md
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat md FILE` for a non-interactive check.
