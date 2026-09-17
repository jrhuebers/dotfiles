# Dotfiles setup knowledge base

This file is the entry point for recreating configurations managed by this
repository. It explains how to maintain the repository knowledge base and
indexes the detailed setup documentation. Host-specific operational
documentation belongs in `~/admin-docs/`, not in this repository.

## Rules for agents

- Before making changes in this repository, run `git pull --ff-only`. If the pull cannot fast-forward cleanly, stop and resolve that first.
- After making changes, verify them, commit the intended files, and push the commit to `origin` before reporting completion. Do not include unrelated working-tree changes.
- For every software install, uninstall, or configuration change, update the relevant file in `docs/` or create one if it does not exist.
- Keep one topic per Markdown file, usually one piece of software or one configuration.
- Document installation, configuration, platform differences, important paths, verification, and removal when relevant. Keep commands copyable and distinguish the repository source from the installed destination.
- Put difficult or multi-step installation/configuration procedures in `docs/`, not in this file.
- Keep this index up to date: every Markdown file under `docs/` must be listed below with a short description.
- After making a change, verify it and update its documentation before reporting completion.

## Knowledge base index

- [`docs/admin-skill.md`](docs/admin-skill.md) — Universal, machine-aware admin skill deployment and verification.
- [`docs/device-profiles.md`](docs/device-profiles.md) — Cluster versus personal-device configuration profiles and on/off matrix.
- [`docs/git.md`](docs/git.md) — Global Git author identity and installation/query commands.
- [`docs/hermes-skills.md`](docs/hermes-skills.md) — Archived Hermes skills boundary, use, promotion, and removal.
- [`docs/glow.md`](docs/glow.md) — Glow Markdown renderer installation and configuration.
- [`docs/open-in-cursor.md`](docs/open-in-cursor.md) — macOS Finder service for opening files and folders in Cursor.
- [`docs/pi-simple-web-tools.md`](docs/pi-simple-web-tools.md) — Pi web-search/fetch extension setup with Exa authentication.
- [`docs/linux-keyboard-layout.md`](docs/linux-keyboard-layout.md) — User-level Linux GNOME/Wayland XKB layout for German characters on a British keyboard.
- [`docs/pi.md`](docs/pi.md) — Pi agent configuration snapshots, deployment, refresh, and verification.
- [`docs/shell.md`](docs/shell.md) — Cluster Bash and personal macOS Zsh startup profiles.
- [`docs/ssh.md`](docs/ssh.md) — Personal SSH client configuration deployment and verification.
- [`docs/tmux.md`](docs/tmux.md) — tmux installation, `.tmux.conf` deployment, reload command, and key settings.
- [`docs/vim.md`](docs/vim.md) — Vim installation and `.vimrc` deployment.
- [`docs/vscode.md`](docs/vscode.md) — VS Code workstation settings deployment and scope.
- [`docs/yazi.md`](docs/yazi.md) — Yazi installation for Fedora/macOS, configuration deployment, package installation, and keybindings.
- [`docs/zed.md`](docs/zed.md) — Zed configuration contents and symlink-based setup.
