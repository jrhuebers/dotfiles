# Shell startup profiles

The tracked shell files are **not** interchangeable. Select the machine profile
in [`device-profiles.md`](device-profiles.md) before deploying either one.

## Bash

`.bashrc` is a portable Bash configuration. It adds `$HOME/.local/bin` to
`PATH` if needed, configures the prompt, enables colored `ls` output, and
provides generic Markdown cleanup (`mdclean`), tmux attachment, and `squeue`
display aliases. It does not override `HOME` or assume a shared filesystem.

From a Linux checkout, install it with:

```sh
install -m 0644 ~/dotfiles/.bashrc ~/.bashrc
bash -n ~/.bashrc
```

After installation, verify it with:

```sh
bash -n ~/.bashrc
bash -ic 'printf "%s\\n" "$PATH"; alias ls mdclean attach squeue'
```

Start a new Bash login session to use it. Verify that the configured path is
appropriate for the current host before replacing any existing shell startup
file.

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
