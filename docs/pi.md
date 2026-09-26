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

To install or remove a package in the live global Pi setup:

```sh
pi install npm:pi-btw
pi install npm:@signalridge/pi-goal
pi install npm:@ogulcancelik/pi-codex-compaction
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The `pi-goal` package is included in both settings profiles; use `/goal` to start or manage a session-scoped autonomous goal. The `pi-codex-compaction` package is included in both profiles and uses OpenAI Codex native remote compaction when an applicable Codex model is active; no additional configuration is required. The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
