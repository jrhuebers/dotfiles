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

`.zshrc` is the macOS profile, including institution-managed work laptops.
It retains macOS-specific `ls -G` and must not be installed unchanged on Linux
or a headless personal server. It adds `~/.local/bin` and the standalone Pi
installer's `~/.pi/agent/bin` to PATH, sources `~/.local/bin/env` only if present,
and includes Antigravity only if installed under the current user's home.
It sets Vim as EDITOR/VISUAL and sources the shared Yazi `y` wrapper, which is
compatible with Zsh as well as Bash.

For Apple Silicon Homebrew, retain this in `~/.zprofile`:

```sh
eval "$(/opt/homebrew/bin/brew shellenv zsh)"
```

Back up existing startup files before deploying. Preserve any local runtime
PATH entries required by your Pi/Node installation.

From a macOS checkout, install it with:

```sh
install -m 0644 ~/dotfiles/.zshrc ~/.zshrc
zsh -n ~/.zshrc
```

Start a new Zsh login session to use it. Verify with:

```sh
zsh -lic 'command -v brew pi python3 yazi md; type y; print -r -- "$EDITOR"'
```

For a noninteractive wrapper smoke test, stub `yazi` to write an existing test
directory to `--cwd-file`, call `y`, and verify `pwd` changes to that directory.
Interactive verification is still needed for terminal keys and previews.

## Removal

Restore a known-good backup or remove only the profile-specific startup file
that was installed. Do not remove a shell startup file on a shared host unless
you have confirmed it is not managed by another mechanism.
