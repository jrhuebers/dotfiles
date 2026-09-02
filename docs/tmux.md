# tmux

The repository's `.tmux.conf` is the shared tmux configuration. The system-level
`~/.tmux.conf` should be a small machine-specific wrapper: source the shared
configuration first, then override only settings that identify the machine.

## Configuration pattern

The ordering is intentional: the repository file supplies the common behavior
(mouse support, extended keys, window and status formatting, red inactive
heavy pane borders, and coloured active-pane indicators without arrows), while
settings after the `source-file`
command identify the machine. In particular,
give each machine a distinct status-bar style so sessions are visually
separable. Keep machine-specific changes small and local to the wrapper rather
than adding them to the shared configuration.

A host wrapper should follow this pattern:

```tmux
# Shared tmux configuration
source-file -q "$HOME/dotfiles/.tmux.conf"

# Choose a style unique to this machine, after the shared configuration.
set -g status-style "bg=colour236,fg=colour255"
```

Use different valid style values on each machine.

## Install and configure

Install tmux with the platform package manager (`sudo apt install tmux` on
Ubuntu, `sudo dnf install tmux` on Fedora, or `brew install tmux` on macOS).
Keep the repository file at its checkout path and create `~/.tmux.conf` as the
machine-specific wrapper; do not replace the wrapper with a direct copy of the
repository file.

After cloning this repository to `~/dotfiles` (or adapting the path in
the wrapper), create the host-specific file:

```sh
cat >~/.tmux.conf <<'EOF'
# Shared tmux configuration
source-file -q "$HOME/dotfiles/.tmux.conf"

# Choose a style unique to this machine.
set -g status-style "bg=colour236,fg=colour255"
EOF
tmux source-file ~/.tmux.conf
```

Reload a running server after changes with `tmux source-file ~/.tmux.conf`.
