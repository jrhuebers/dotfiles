# md

`md` is a small compiled Markdown viewer for terminal use. It renders Markdown
and sends it to a pager; it has no Glow or configuration-file dependency.

The renderer hardcodes Glow's LightStyle colors, one space of left and right
margin, no mouse handling, pager mode, no file browser when files are supplied,
and reflow of single newlines while retaining paragraph breaks. The pager is
`$PAGER`, or `less -R` when `$PAGER` is unset.

When given a directory—or no argument from an interactive terminal—`md` opens a
small keyboard file picker. It recursively lists visible Markdown files while
skipping hidden files and directories. Use arrow keys or `j`/`k`, press Enter
to open a file, or `q` to quit.

## Build and install on Linux

The source is [`tools/md.rs`](../tools/md.rs). It only uses the Rust standard
library and builds to a native user-local binary:

```sh
mkdir -p ~/.local/bin
rustc -O -C strip=symbols ~/dotfiles/tools/md.rs -o ~/.local/bin/md
```

Keep `~/.local/bin` in `PATH`. Verify the installation with:

```sh
md --version
md README.md
md .
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat` for a non-interactive smoke test. The command accepts one or
more Markdown paths; `-` reads standard input.

## Removal

```sh
rm -f ~/.local/bin/md
```
