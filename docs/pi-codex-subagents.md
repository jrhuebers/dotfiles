# Pi Codex subagents

The `pi-codex-subagents` extension stores its optional configuration at `~/.pi/agent/pi-codex-subagents/config.json`.

The cluster profile keeps the source copy at `pi/cluster/pi-codex-subagents/config.json`. It allowlists the configured OpenAI Codex and EPFL models for per-task routing, and also permits models selected through Pi's enabled-model scope. Models unavailable on a particular host are ignored by the extension with a warning.

Deploy the cluster configuration with:

```sh
mkdir -p ~/.pi/agent/pi-codex-subagents
cp -p ~/dotfiles/pi/cluster/pi-codex-subagents/config.json ~/.pi/agent/pi-codex-subagents/config.json
```

Restart Pi after changing the file. A new session should expose `model` and `thinking` on `spawn_agent`; the model values are provider-qualified, for example `openai-codex/gpt-5.6-sol` or `epfl/zai-org/GLM-5.3`.

To remove the per-task model allowlist and return to template/parent-model routing, remove `~/.pi/agent/pi-codex-subagents/config.json` and restart Pi.
