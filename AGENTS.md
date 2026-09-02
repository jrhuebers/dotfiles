# Dotfiles setup knowledge base

This file is the entry point for recreating configurations managed by this
repository. It explains how to maintain the repository knowledge base and
indexes the detailed setup documentation. Host-specific operational
documentation belongs in `~/admin-docs/`, not in this repository.

## Rules for agents

- For every software install, uninstall, or configuration change, update the relevant file in `docs/` or create one if it does not exist.
- Keep one topic per Markdown file, usually one piece of software or one configuration.
- Document installation, configuration, platform differences, important paths, verification, and removal when relevant. Keep commands copyable and distinguish the repository source from the installed destination.
- Put difficult or multi-step installation/configuration procedures in `docs/`, not in this file.
- Keep this index up to date: every Markdown file under `docs/` must be listed below with a short description.
- After making a change, verify it and update its documentation before reporting completion.

## Knowledge base index

- [`docs/git.md`](docs/git.md) — Global Git author identity and installation/query commands.
- [`docs/open-in-cursor.md`](docs/open-in-cursor.md) — macOS Finder service for opening files and folders in Cursor.
- [`docs/gnome-keyboard-layout.md`](docs/gnome-keyboard-layout.md) — User-level GNOME/Wayland XKB layout for German characters on a British keyboard.
- [`docs/pi.md`](docs/pi.md) — Pi agent configuration snapshots, deployment, refresh, and verification.
- [`docs/tmux.md`](docs/tmux.md) — tmux installation, `.tmux.conf` deployment, reload command, and key settings.
- [`docs/vim.md`](docs/vim.md) — Vim installation and `.vimrc` deployment.
- [`docs/yazi.md`](docs/yazi.md) — Yazi installation for Fedora/macOS, configuration deployment, package installation, and keybindings.
- [`docs/zed.md`](docs/zed.md) — Zed configuration contents and symlink-based setup.
