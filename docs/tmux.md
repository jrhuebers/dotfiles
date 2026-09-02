# tmux

The repository's `.tmux.conf` is the tmux configuration.

## Install and configure

Install tmux with the platform package manager (`sudo dnf install tmux` on Fedora or `brew install tmux` on macOS), then copy the configuration:

```sh
cp .tmux.conf ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

The configuration enables mouse support and extended key reporting (`csi-u`), and uses a yellow status bar. Reload a running server after changes with `tmux source-file ~/.tmux.conf`.
