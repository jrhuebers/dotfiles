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

For Linux x86_64, install the official release archive after verifying its
published SHA-256 checksum:

```sh
version=0.6.39
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

If `rustc` is already available, building from the checked-out source is also
supported:

```sh
mkdir -p ~/.local/bin
rustc -O -C strip=symbols ~/md/tools/md.rs -o ~/.local/bin/md
mkdir -p ~/.config
ln -sfn ~/md/.config/md.yaml ~/.config/md.yaml
```

The viewer uses `$PAGER` when set and otherwise `less -R`. LaTeX-to-Unicode
rendering is enabled by default and can be disabled with `render_latex: false`
in `~/.config/md.yaml`.

## Verify

```sh
md --version
md README.md
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat md FILE` for a non-interactive check.
