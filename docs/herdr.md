# Herdr

Herdr is the standard terminal multiplexer for all supported dotfiles
profiles—cluster hosts, personal Linux and macOS machines, and personal
headless servers—for organizing coding-agent workspaces, tabs, and panes. It is
installed per user; on the documented Fedora host the binary is
`~/.local/bin/herdr` and the stable `0.9.1` client/server is currently running.
Use the same configuration and workflow on every supported host, adapting only
the platform-specific installation step.

## Install

On a Linux cluster without system package privileges, use Herdr's official
user-local installer:

```sh
curl -fsSL https://herdr.dev/install.sh | sh
herdr --version
```

The installer places the binary in `~/.local/bin`; ensure that directory is in
`PATH`. Do not run the installer from a shared system account or replace a
package-managed installation.

## Current configuration

The live configuration is at `~/.config/herdr/config.toml`. It is currently
managed locally rather than symlinked from this repository. The explicit
settings are:

```toml
onboarding = false

[theme]
name = "tokyo-night-day"
auto_switch = false

[ui]
status_indicators = "symbols"

[ui.toast]
delivery = "off"

[ui.sound]
enabled = true

[keys]
prefix = "ctrl+f"
```

All other Herdr options, including prefix-mode actions and terminal behavior,
use their application defaults. The Herdr leader/prefix is therefore **Ctrl+F**;
for example, prefix-mode commands are entered as `Ctrl+F` followed by the
configured action key.

## Applying and verifying configuration

After editing the live configuration, validate and apply it to the running
server:

```sh
herdr config check
herdr server reload-config
herdr status
```

The server socket and logs are under `~/.config/herdr/`. Do not commit session
state, logs, or other generated files.
