# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps separate settings profiles because a compute cluster has Slurm tools that
should not be enabled on personal machines:

- `pi/cluster/settings.json` → `~/.pi/agent/settings.json` on a cluster host.
- `pi/personal/settings.json` → `~/.pi/agent/settings.json` on a laptop,
  desktop PC, or personal server such as the Oracle server.

The cluster profile includes two packages that are not in the personal profile:
`git:github.com/jrhuebers/pi-slurm` and `npm:pi-subagents`. Both profiles include
`git:github.com/jrhuebers/pi-whoami`, `npm:@signalridge/pi-goal`,
`npm:@ogulcancelik/pi-codex-compaction`, and
`npm:@ogulcancelik/pi-codex-subagents`. Codex subagents are enabled in both
profiles; `pi-subagents` remains cluster-only. The goal package provides the
session-scoped `/goal` command and `goal_complete`, `goal_blocked`, and
`goal_wait` tools for autonomous, verifiable
completion. Other Pi settings and packages are currently identical, including
`npm:pi-simple-web-tools@0.1.0`. The web-tools credential is user-local and
secret-bearing; follow
[`pi-simple-web-tools.md`](pi-simple-web-tools.md) rather than tracking it here.
See [`device-profiles.md`](device-profiles.md) for the complete cluster/personal
split across this repository.

## Runtime extension profiles

The live cluster setup keeps the ordinary Pi launcher at `~/.local/bin/pi` and provides separate profile commands at `~/.local/bin/pi-research` and `~/.local/bin/pi-basic`, backed by `~/.local/libexec/pi-profile`. Do not pass profile names as flags to the ordinary `pi` command.

`pi-research` sets `PI_CODING_AGENT_DIR` to the dedicated `~/.pi/research` user agent directory and uses normal extension/resource discovery **except skills**. It passes `--no-skills` and explicitly loads only the `admin` and `hpc-cluster` skill directories, which are symlinked into `~/.pi/research/skills/`; other user, project, and package skills are excluded. The profile has separate settings and session storage, while user-local model and authentication files, installed package stores, and extensions may be linked to the ordinary `~/.pi/agent` installation. `SYSTEM.md`, its referenced guidelines, and editable advisor/editor/reviewer role sources under `~/.pi/research/agents/` are **copies** in `~/.pi/research`, not symlinks to a prompt checkout. Edit the copies there; refresh them manually if desired. Pi loads `SYSTEM.md` as the research system prompt, and the research-only `research-system-includes.ts` extension replaces each local `@file.md` line with that file's contents in place in the system-prompt preamble at each turn (ordinary pi-context-include only handles `AGENTS.md`). The wrapper loads that extension explicitly through the research profile JSON. The wrapper runs `compile-agent-prompts.py` before launching Pi; it replaces `@file.md` lines in each role source in place and writes generated runtime templates to `~/.pi/research/pi-codex-subagents/agents/`. The research extension rebuilds these runtime templates again immediately before each `spawn_agent` call, so role/guideline edits take effect in live parent sessions. Edit the sources under `~/.pi/research/agents/`, not the generated runtime files. pi-codex-subagents disables context-file and extension discovery in children, so they receive the expanded role text as part of the child task, not as an AGENTS.md include. The advisor defaults to `openai-codex/gpt-6-sol` at medium thinking; its `read`, `grep`, `find`, and `ls` allowlist names are Pi built-in tools, even if another session exposes a different tool set. Keep secrets user-local and never commit `auth.json` or `models.json`.

The installed `git:github.com/jrhuebers/pi-context-viewer` package is the user-owned `/context` fork. After a model request, its System and Full tabs replay the active branch's persisted system prompt, including in-place `@` expansions, instead of falling back to the unexpanded `SYSTEM.md` source when Pi is idle. Before the first request there is no persisted system prompt to replay, so `/context` may show the unexpanded pre-run source; Payload remains the exact captured provider request.

`pi-basic` disables discovered extensions, prompt templates, and themes, then explicitly loads the configured allowed extensions; it leaves skill discovery enabled so all user, project, and package skills remain available.

The basic profile intentionally excludes `pi-slurm` and `pi-btw` extensions, while retaining skills supplied by those packages. It must explicitly load `@ogulcancelik/pi-codex-subagents` from the local package store because it disables extension discovery.

The installed profile definitions are `~/.pi/profiles/basic.json` and `~/.pi/profiles/research.json`; the wrapper requires `jq` and forwards ordinary Pi CLI flags unchanged. A profile's optional `agentDir` key selects an existing absolute directory (or `~/` path) through `PI_CODING_AGENT_DIR`; it does not redirect a working directory's project `.pi/` configuration. Without `agentDir`, the default user agent directory remains in use. The research settings are independent of the ordinary settings, so synchronize non-secret package/settings changes deliberately rather than assuming they propagate.

The basic profile JSON currently uses absolute paths into the local Pi package store, so regenerate or adapt its extension paths when deploying this setup to another machine rather than copying them unchanged. The research profile's copied prompts, restricted skill links, and shared package/model links must likewise be provisioned per host. Verify the selection with `pi-research --version`, `pi-research --list-models GLM-5.3-Flash`, and a short prompt checking that the local research guidelines, only two allowed skills, and three role templates are visible. To revert the research profile without deleting sessions, remove `agentDir` from its profile JSON.

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

On a fresh workstation with an already-working Pi setup, preserve the local
`deviceId`, `lastChangelogVersion`, `defaultProvider`, and `defaultModel` when
merging the personal profile. The tracked model is a snapshot and may not be
available to the new machine's account; do not overwrite working authentication
or force an unavailable model. Keep this merged settings file local, rather
than refreshing the repository snapshot from it.

For current installer-managed Pi, reconcile configured packages with
`pi update --extensions` (plain `pi update` updates Pi itself), then `pi list`.
Pinned packages may require an explicit `pi install SOURCE` on a fresh machine.
Verify `pi --help` for startup diagnostics without making an AI request. Existing
Node.js from the standalone Pi installer may be used; verify `node` and `npm`
are available in a new login shell.

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
pi install npm:@ogulcancelik/pi-codex-subagents
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The `pi-goal` package is included in both settings profiles; use `/goal` to start or manage a session-scoped autonomous goal. The `pi-codex-compaction` package is included in both profiles and uses OpenAI Codex native remote compaction when an applicable Codex model is active; no additional configuration is required. The `pi-codex-subagents` package is included in both profiles; configure its model routing with [`pi-codex-subagents.md`](pi-codex-subagents.md). The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
