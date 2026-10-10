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

## Background Bash in children

The shared `pi/shared/pi-codex-subagents/config.json` explicitly loads the background-task extension in children through `defaults.extensions`:

```json
{
  "defaults": {
    "extensions": [
      "~/.pi/agent/git/github.com/jrhuebers/pi-background-tasks/index.ts"
    ]
  }
}
```

Install the prerequisite in the ordinary Pi agent directory before deploying this config:

```sh
PI_CODING_AGENT_DIR="$HOME/.pi/agent" pi install git:github.com/jrhuebers/pi-background-tasks
test -f "$HOME/.pi/agent/git/github.com/jrhuebers/pi-background-tasks/index.ts"
```

The installed path is Pi's user-global Git package checkout, not a path inside dotfiles. This default intentionally shares that extension with separate agent directories; if its installed location differs, adjust `defaults.extensions`. Missing paths fail agent creation rather than installing packages automatically.

Children receive the overridden `bash` tool (`run_in_background`, `background_after_seconds`, `max_run_seconds`, and `notify_on_exit`) plus `jobs` for listing, cancelling, and extending jobs. The foreground handoff delay comes from the installed extension's `config.yaml`; `max_run_seconds` remains optional. This prevents a slow command from indefinitely blocking the tool batch, but does not itself stop a buggy command that runs in the background. Use a finite lifetime for potentially wedged commands.

When a template omits `tools`, configured extensions cause normal child tool activation instead of copying the parent's tool-name list. A template with an explicit tool allowlist must include both `bash` and `jobs` to expose background execution and its controls. Preserve intentional read-only allowlists. A template's `extensions` replace these defaults; include the background extension there too if that template needs it.

Children are terminated after final completion or interruption, and ordinary shutdown cancels their managed background jobs. A child must finish or cancel required jobs before returning its final answer; these are not detached cluster workloads. Use Slurm for substantial work on shared cluster hosts.

Changes to defaults apply to newly spawned agent records without restarting Pi. Existing records retain their saved extension paths, including when continued with `send_message`; start a new task to adopt the defaults. To disable this for future children, remove only the background-task entry from `defaults.extensions`.

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
