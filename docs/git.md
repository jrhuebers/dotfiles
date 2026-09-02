# Git identity

`.gitconfig` stores the global Git author name and email.

## Install

After cloning the repository:

```sh
cp .gitconfig ~/.gitconfig
```

A repository-local `.git/config` can override these global values and is not synced with the remote.

## Query

```sh
git config --global --list --show-origin
git config --show-origin --show-scope --get-regexp '^user\.'
```
