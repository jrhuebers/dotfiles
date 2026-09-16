# Shell startup profiles

The tracked shell files are **not** interchangeable. Select the machine profile
in [`device-profiles.md`](device-profiles.md) before deploying either one.

## Cluster Bash

`.bashrc` is for the cluster profile only. It deliberately sets the cluster
home directory and user-local binary path, and adds the cluster tmux helper.
Do not copy it to a laptop, desktop, or personal server.

From a cluster-host checkout, install it with:

```sh
install -m 0644 ~/dotfiles/.bashrc ~/.bashrc
bash -n ~/.bashrc
```

Start a new Bash login session to use it. Verify that the configured home and
path are appropriate for the current host before replacing any existing shell
startup file.

## Personal macOS Zsh

`.zshrc` is the personal macOS profile. It contains macOS-specific paths and
must not be installed unchanged on Linux or a headless personal server.

From a macOS checkout, install it with:

```sh
install -m 0644 ~/dotfiles/.zshrc ~/.zshrc
zsh -n ~/.zshrc
```

Start a new Zsh login session to use it. Before deployment, review the
machine-local tool paths in the tracked file; retain or replace them only when
they exist on that Mac.

## Removal

Restore a known-good backup or remove only the profile-specific startup file
that was installed. Do not remove a shell startup file on a shared host unless
you have confirmed it is not managed by another mechanism.
