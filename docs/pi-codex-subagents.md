# Pi Codex subagents

The `pi-codex-subagents` extension stores its optional configuration at `~/.pi/agent/pi-codex-subagents/config.json`.

The cluster profile keeps the source copy at `pi/cluster/pi-codex-subagents/config.json`. It allowlists the configured OpenAI Codex and EPFL models for per-task routing, and also permits models selected through Pi's enabled-model scope. Models unavailable on a particular host are ignored by the extension with a warning.

The ordinary `pi` and `pi-basic` commands both use `~/.pi/agent/pi-codex-subagents/config.json`; `pi-basic` does not select another agent directory. `pi-research` uses `~/.pi/research`, whose config is a symlink to the ordinary config so routing stays synchronized. Deploy the source and link the research profile with:

```sh
mkdir -p ~/.pi/agent/pi-codex-subagents ~/.pi/research/pi-codex-subagents
cp -p ~/dotfiles/pi/cluster/pi-codex-subagents/config.json ~/.pi/agent/pi-codex-subagents/config.json
rm -f ~/.pi/research/pi-codex-subagents/config.json
ln -s "$HOME/.pi/agent/pi-codex-subagents/config.json" ~/.pi/research/pi-codex-subagents/config.json
```

Restart the relevant Pi command after changing the file. A new session should expose `model` and `thinking` on `spawn_agent`; the model values are provider-qualified, for example `openai-codex/gpt-5.6-sol` or `epfl/zai-org/GLM-5.3`.

To remove the per-task model allowlist and return to template/parent-model routing, remove `~/.pi/agent/pi-codex-subagents/config.json` and its research-profile symlink, then restart Pi.
