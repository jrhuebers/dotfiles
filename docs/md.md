# md

`md` is the primary Markdown viewer for this setup. It is maintained in the
standalone public repository:

<https://github.com/jrhuebers/md>

It replaces Glow for everyday Markdown viewing. Glow may remain installed for
reference or comparison, but it is not the configured viewer.

## Install

Clone or update the standalone repository, then compile the user-local binary:

```sh
git clone https://github.com/jrhuebers/md.git ~/md
mkdir -p ~/.local/bin
rustc -O -C strip=symbols ~/md/tools/md.rs -o ~/.local/bin/md
mkdir -p ~/.config
ln -sfn ~/md/.config/md.yaml ~/.config/md.yaml
```

`md` prefers the `lessi` pager when it is installed and falls back to `less -R`:

```sh
sudo dnf install cargo
cargo install lessi --locked --root ~/.local
```

The viewer can also use another pager through `$PAGER`. LaTeX-to-Unicode
rendering is enabled by default and can be disabled with `render_latex: false`
in `~/.config/md.yaml`.

## Verify

```sh
md --version
md README.md
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat md FILE` for a non-interactive check.
