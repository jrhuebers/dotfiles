# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps separate settings profiles because a compute cluster has Slurm tools that
should not be enabled on personal machines:

- `pi/cluster/settings.json` → `~/.pi/agent/settings.json` on a cluster host.
- `pi/personal/settings.json` → `~/.pi/agent/settings.json` on a laptop,
  desktop PC, or personal server such as the Oracle server.

The cluster profile enables one package that is not in the personal profile:
`git:github.com/jrhuebers/pi-slurm`. Both profiles include
`git:github.com/jrhuebers/pi-whoami`, `npm:@signalridge/pi-goal`,
`npm:pi-subagents`, and `npm:@ogulcancelik/pi-codex-compaction`. The goal package provides the
session-scoped `/goal` command and `goal_complete`, `goal_blocked`, and
`goal_wait` tools for autonomous, verifiable
completion. All other Pi settings and packages are currently identical, including
`npm:pi-simple-web-tools@0.1.0`. The web-tools credential is user-local and secret-bearing; follow
[`pi-simple-web-tools.md`](pi-simple-web-tools.md) rather than tracking it here.
See [`device-profiles.md`](device-profiles.md) for the complete cluster/personal
split across this repository.

## Runtime extension profiles

The live cluster setup provides named runtime profiles through a user-local wrapper at `~/.local/bin/pi`; the original Pi launcher is preserved as `~/.local/bin/pi.real`.

`pi --research` sets `PI_CODING_AGENT_DIR` to the dedicated `~/.pi/research` user agent directory and uses normal Pi resource discovery. This profile contains separate settings and session storage; user-local model and authentication files, installed package stores, skills, and extensions may be linked to the ordinary `~/.pi/agent` installation. Its `AGENTS.md` loads a separately maintained research-prompt collection through the context-include extension, and its `pi-codex-subagents/agents/` directory exposes reviewer/editor templates. The profile's settings must allow the prompt collection's path for context includes; child templates must explicitly read any guidelines they need because pi-codex-subagents disables context-file discovery in children. Keep secrets user-local and never commit `auth.json` or `models.json`.

`pi --basic` disables discovered extensions, prompt templates, and themes, then explicitly loads the configured allowed extensions; it leaves skill discovery enabled so all user, project, and package skills remain available.

The basic profile intentionally excludes `pi-slurm`, `pi-subagents`, and `pi-btw` extensions, while retaining skills supplied by those packages.

The installed profile definitions are `~/.pi/profiles/basic.json` and `~/.pi/profiles/research.json`; the wrapper requires `jq` and forwards ordinary Pi CLI flags unchanged. A profile's optional `agentDir` key selects an existing absolute directory (or `~/` path) through `PI_CODING_AGENT_DIR`; it does not redirect a working directory's project `.pi/` configuration. Without `agentDir`, the default user agent directory remains in use. The research settings are independent of the ordinary settings, so synchronize non-secret package/settings changes deliberately rather than assuming they propagate.

The basic profile JSON currently uses absolute paths into the local Pi package store, so regenerate or adapt its extension paths when deploying this setup to another machine rather than copying them unchanged. The research profile and its symlinked prompt collection must likewise be provisioned per host. Verify the selection with `pi --research --version`, `pi --research --list-models GLM-5.3-Flash`, and a short prompt checking that the research guidelines and role templates are visible. To revert the research profile without deleting sessions, remove `agentDir` from its profile JSON.

## Refresh the repository copies

Set `PI_PROFILE` to the profile used by the live machine before refreshing:

```sh
PI_PROFILE=personal  # use cluster on a cluster host
mkdir -p ~/dotfiles/pi/$PI_PROFILE
cp -p ~/.pi/agent/settings.json ~/dotfiles/pi/$PI_PROFILE/settings.json
```

## Install Pi on a no-sudo Ubuntu cluster host

Pi requires Node.js `>=22.19.0`. When the cluster does not provide Node.js or
sudo, install the official Linux x86_64 Node.js 22 archive under `~/.local/opt`
and link `node`, `npm`, and `npx` into `~/.local/bin`. Verify the archive with
the matching SHA-256 entry from Node.js `SHASUMS256.txt`. Then install Pi
user-locally:

```sh
npm install --prefix "$HOME/.local" --global @earendil-works/pi-coding-agent
pi --version
```

Do not copy `~/.pi/agent/auth.json`, `models.json`, session files, or provider
credentials between machines. Configure authentication separately on the
cluster if permitted.

## Deploy the repository copies

From a checkout at `~/dotfiles`, select exactly one profile:

```sh
PI_PROFILE=personal  # use cluster on a cluster host
case "$PI_PROFILE" in cluster|personal) ;; *) exit 2 ;; esac
mkdir -p ~/.pi/agent
cp -p ~/dotfiles/pi/$PI_PROFILE/settings.json ~/.pi/agent/settings.json
```

Do not install the cluster profile on a personal device: it registers Slurm
commands that are unavailable or inappropriate there. Restart Pi after
configuration changes so it reloads the files. Verify the selected profile with:

```sh
cmp -s ~/dotfiles/pi/$PI_PROFILE/settings.json ~/.pi/agent/settings.json && \
  echo "Pi $PI_PROFILE configuration copy matches."
```

Do not add authentication tokens or other secrets to the tracked configuration.

## Install the paper-fetching skill

The portable source bundle is `~/dotfiles/skills/paper-fetching/`; install it into Pi's user skill directory as a symlink so `SKILL.md` and its helper scripts stay together and updates to the checkout are immediately visible:

```sh
mkdir -p ~/.pi/agent/skills
ln -s ~/dotfiles/skills/paper-fetching ~/.pi/agent/skills/paper-fetching
```

If the link already exists, inspect it rather than replacing an unrelated skill. Verify with `readlink ~/.pi/agent/skills/paper-fetching` and confirm `SKILL.md` plus `scripts/fetch_papers.py` are readable. Start a new Pi session or use `/reload` in the current session. Invoke with `/skill:paper-fetching`; the helper commands and prerequisites are documented in the skill itself. To uninstall, remove only the user skill symlink: `rm ~/.pi/agent/skills/paper-fetching`.

To install or remove a package in the live global Pi setup:

```sh
pi install npm:pi-btw
pi install npm:@signalridge/pi-goal
pi install npm:@ogulcancelik/pi-codex-compaction
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The `pi-goal` package is included in both settings profiles; use `/goal` to start or manage a session-scoped autonomous goal. The `pi-codex-compaction` package is included in both profiles and uses OpenAI Codex native remote compaction when an applicable Codex model is active; no additional configuration is required. The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
