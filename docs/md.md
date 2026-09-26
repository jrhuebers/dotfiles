# md

`md` is a small compiled Markdown viewer for terminal use. It deliberately has
only one display mode: render Markdown and send it to a pager. It does not use
Glow, a TUI, or a configuration file.

The renderer hardcodes the settings previously used for Glow: light terminal
styling, no mouse handling, pager mode enabled, no file browser, and reflow of
single newlines while retaining paragraph breaks. The pager is `$PAGER`, or
`less -R` when `$PAGER` is unset.

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
printf '# Heading\n\nMarkdown from stdin.\n' | md -
```

Use `PAGER=cat` for a non-interactive smoke test. The command accepts one or
more Markdown paths; `-` reads standard input.

## Removal

```sh
rm -f ~/.local/bin/md
```
