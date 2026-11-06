# uv

`uv` is Astral's fast Python package and project manager. It is a required baseline tool: install it on every machine, including personal workstations and cluster accounts. Use a user-local installation on shared systems; do not install or configure it system-wide on clusters.

## Install

macOS with Homebrew:

```sh
brew install uv
```

Linux and other supported Unix-like systems without an appropriate package manager, install into the current user's home using Astral's official installer:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Use the native package manager on other platforms when appropriate. Ensure the install directory (normally `~/.local/bin`) is on `PATH`; the tracked shell profiles add user-local binaries where they are maintained. On Apple Silicon use native Homebrew under `/opt/homebrew`.

## Verify

```sh
command -v uv
uv --version
uv --help
```

No Python installation or global Python package configuration is required for uv itself.

## Remove

For Homebrew:

```sh
brew uninstall uv
```

For the standalone installer, remove only the uv/uvx binaries and uv shell-completion files it installed in the user's home (normally under `~/.local/bin` and `~/.local/share`). uv does not provide a `uv self uninstall` command. Do not remove project environments or caches as part of uninstalling the executable.
