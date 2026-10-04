# Pi Codex subagents

The `@ogulcancelik/pi-codex-subagents` Pi extension provides `spawn_agent`,
`wait_agent`, steering, and agent-browsing tools. It is distinct from
`npm:pi-subagents`. The Codex extension is included in both Pi settings
profiles (`pi/personal/settings.json` and `pi/cluster/settings.json`) and should
be enabled on every supported machine.

## Install and enable

Reconcile the profile's package list with Pi, or install directly:

```sh
pi update --extensions
# or: pi install npm:@ogulcancelik/pi-codex-subagents
pi list
```

If a runtime disables extension discovery (for example `pi-basic` with
`--no-extensions`), explicitly load the installed extension from its local
package path in that runtime's allowlist. A normal Pi session loads it from
`settings.json`. Restart Pi after installation or settings changes.

## Model-routing configuration

The shared, non-secret model-routing configuration is tracked at
`pi/shared/pi-codex-subagents/config.json`. Deploy it under the agent directory
used by each Pi runtime:

```sh
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
mkdir -p "$AGENT_DIR/pi-codex-subagents"
cp -p ~/dotfiles/pi/shared/pi-codex-subagents/config.json \
  "$AGENT_DIR/pi-codex-subagents/config.json"
```

The config allowlists the repository's OpenAI Codex and EPFL models and also
permits models selected through Pi's enabled-model scope. Unavailable models
are ignored with a warning. Review the list against the providers/models
available on a given machine; credentials and model endpoints remain local and
must not be tracked.

For separate agent directories such as `~/.pi/research`, install the config
there as well or link its `pi-codex-subagents/config.json` to the ordinary
agent directory's config. `pi-basic` uses the ordinary agent directory, so it
shares the regular config; its explicit extension allowlist must still include
the package because discovery is disabled.

A fresh Pi session should expose `model` and `thinking` on `spawn_agent` when
eligible configured models are available. Example model identifiers include
`openai-codex/gpt-5.6-sol` and `epfl/zai-org/GLM-5.3`.

## Removal

Remove the package from the active agent profile and uninstall it from Pi:

```sh
pi remove npm:@ogulcancelik/pi-codex-subagents
```

Remove only the corresponding
`$AGENT_DIR/pi-codex-subagents/config.json` if you also want to discard the
model-routing allowlist. For separate research or profile directories, remove
only their associated config/link. Existing session data is not removed by
these steps.
