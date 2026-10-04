# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps separate settings profiles because a compute cluster has Slurm tools that
should not be enabled on personal machines:

- `pi/cluster/settings.json` → `~/.pi/agent/settings.json` on a cluster host.
- `pi/personal/settings.json` → `~/.pi/agent/settings.json` on a laptop,
  desktop PC, or personal server such as the Oracle server.

The cluster profile includes `git:github.com/jrhuebers/pi-slurm`, which is not in the personal profile. The retired `npm:pi-subagents` package is removed from both profiles. Both profiles include
`git:github.com/jrhuebers/pi-whoami`, `npm:@signalridge/pi-goal`,
`npm:@ogulcancelik/pi-codex-compaction`, and
`npm:@ogulcancelik/pi-codex-subagents`. Codex subagents are enabled in both
profiles. Both profiles preserve the four-line mouse-wheel scroll setting. The goal package provides the
session-scoped `/goal` command and `goal_complete`, `goal_blocked`, and
`goal_wait` tools for autonomous, verifiable
completion. Other Pi settings and packages are currently identical, including
`npm:pi-simple-web-tools@0.1.0`. The web-tools credential is user-local and
secret-bearing; follow
[`pi-simple-web-tools.md`](pi-simple-web-tools.md) rather than tracking it here.
See [`device-profiles.md`](device-profiles.md) for the complete cluster/personal
split across this repository.

## Runtime extension profiles

The ordinary Pi launcher remains at `~/.local/bin/pi`. `pi-basic` continues to use `~/.local/libexec/pi-profile` and its local `~/.pi/profiles/basic.json`. The complete research environment is now distributed separately through [`jrhuebers/pi-research`](https://github.com/jrhuebers/pi-research); follow that repository's README for a versioned Git checkout, user-local `scripts/setup`, configuration, and `pi-research doctor`. Do not pass profile names as flags to ordinary Pi.

The portable research launcher selects the dedicated `~/.pi/research` agent directory (or `PI_RESEARCH_AGENT_DIR` override), preserves normal resource discovery except skills, and explicitly loads the local `profile.json` skill allowlist. Fresh profiles enable only portable `admin` and `hpc-cluster` skills. Shipped guidelines/role sources synchronize into runtime copies, with local `overrides/prompts/` and `overrides/agents/` layered above them. `cluster.md`, settings, model choices, authentication, and sessions remain local. The include extension expands system guidance in place; the compiler builds advisor/editor/reviewer runtime templates before launch and immediately before spawning. Never edit generated templates. Default roles inherit the parent model; configure model-specific local overrides only after checking availability. Keep credentials user-local and never commit `auth.json` or `models.json`.

The installed `git:github.com/jrhuebers/pi-context-viewer` package is the user-owned `/context` fork. After a model request, its System and Full tabs replay the active branch's persisted system prompt, including in-place `@` expansions, instead of falling back to the unexpanded `SYSTEM.md` source when Pi is idle. Before the first request there is no persisted system prompt to replay, so `/context` may show the unexpanded pre-run source; Payload remains the exact captured provider request.

`pi-basic` disables discovered extensions, prompt templates, and themes, then explicitly loads the configured allowed extensions; it leaves skill discovery enabled so all user, project, and package skills remain available.

The basic profile intentionally excludes `pi-slurm` and `pi-btw` extensions, while retaining skills supplied by those packages. It must explicitly load `@ogulcancelik/pi-codex-subagents` from the local package store because it disables extension discovery.

The basic wrapper still requires `jq` and forwards Pi CLI flags unchanged. Its optional `agentDir` selects a user agent directory, not project `.pi/` configuration. Regenerate its package-store paths per machine. The portable research launcher instead requires Python 3.10+, Node.js 22.19+, and Pi 0.99.2+; its setup preserves existing local settings on explicit adoption and never imports credentials automatically. Research and ordinary settings remain independent. Verify with `pi-research doctor`, `pi-research --version`, and a model lookup appropriate to the target machine; use local documentation and live read-only queries to establish relevant cluster facts; the local `cluster.md` notes are optional, not a mandatory checklist. Follow the portable repository's upgrade/rollback instructions rather than changing the retired research profile JSON.

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
