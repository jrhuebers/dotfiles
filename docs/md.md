# md

`md` is the primary Markdown viewer for this setup. It is maintained in the
standalone public repository:

<https://github.com/jrhuebers/md>

It replaces Glow for everyday Markdown viewing. Glow may remain installed for
reference or comparison, but it is not the configured viewer.

## Install

The standalone repository is available for source builds and development:

```sh
git clone https://github.com/jrhuebers/md.git ~/md
```

For Linux x86_64, install the current official release archive after verifying its published SHA-256 checksum. The archive includes the binary, bundled renderer, and default configuration:

```sh
version=0.8.0
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
ln -sfn ~/.local/opt/md-${version}/share/md/md.yaml ~/.config/md.yaml
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

The archive includes the Node.js math bridge and vendored renderer. Keep Node.js in `PATH` for full math rendering. The same Cargo build works on supported Linux platforms with Rust installed. To remove this installation, remove only `~/.local/bin/md` and the `~/.config/md.yaml` symlink.

The viewer uses its built-in interactive pager when `$PAGER` is unset, or the specified external pager when set (for example, `PAGER='less -R' md FILE`). LaTeX-to-Unicode rendering is enabled by default and can be disabled with `render_latex: false` in `~/.config/md.yaml`.

## Verify

```sh
md --version
md README.md
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat md FILE` for a non-interactive check.
