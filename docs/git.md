# Git identity and GitHub CLI

Git and the GitHub CLI (`gh`) are required baseline tools on every supported
machine profile. `.gitconfig` stores the global Git author name and email. It
also rewrites HTTP(S) GitHub URLs to the SSH transport, so clones and remote
operations use `git@github.com:` by default.

## Install

After cloning the repository:

```sh
cp .gitconfig ~/.gitconfig
```

Install `gh` on every machine. Use the native package manager when available;
on a no-sudo Linux cluster, download the official `linux_amd64` release archive
and its matching checksum from the [GitHub CLI releases](https://github.com/cli/cli/releases),
extract it under `~/.local/opt`, and link `gh` into `~/.local/bin`:

```sh
version=<version>
target="$HOME/.local/opt/gh-$version"
mkdir -p ~/.local/bin "$target"
# Download gh_<version>_linux_amd64.tar.gz and gh_<version>_checksums.txt.
# Verify the archive with the matching line from the checksum file, then:
tar -xzf gh_${version}_linux_amd64.tar.gz -C "$target" --strip-components=1
install -m 0755 "$target/bin/gh" ~/.local/bin/gh
gh --version
```

On macOS with Homebrew, run `brew install gh` and `gh auth login` as the user.
Verify `gh --version` and `gh api user --jq .login`. On Apple Silicon Homebrew
is under `/opt/homebrew`; ensure its `bin` directory is in PATH. Git provided
by Apple's Command Line Tools can be retained if already working.

Back up `~/.gitconfig` before copying the tracked identity. The repository email
is a personal address; use a repository-local `user.email` override for work
projects if institutional policy requires it. Verify GitHub SSH authentication
before relying on the HTTP-to-SSH rewrite. Never bypass host-key verification.

A repository-local `.git/config` can override these global values and is not synced with the remote.

On a shared cluster without GitHub SSH authentication, an HTTPS checkout can
be refreshed without the global URL rewrite for that command:

```sh
GIT_CONFIG_GLOBAL=/dev/null git -C ~/dotfiles pull --ff-only
```

## Query

```sh
git config --global --list --show-origin
git config --show-origin --show-scope --get-regexp '^user\.'
git config --global --get-regexp '^url\.'
```
