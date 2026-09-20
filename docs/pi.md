# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps separate settings profiles because a compute cluster has Slurm tools that
should not be enabled on personal machines:

- `pi/cluster/settings.json` → `~/.pi/agent/settings.json` on a cluster host.
- `pi/personal/settings.json` → `~/.pi/agent/settings.json` on a laptop,
  desktop PC, or personal server such as the Oracle server.

The cluster profile enables two packages that are not in the personal profile:
`git:github.com/jrhuebers/pi-slurm` and `npm:pi-subagents`. Both profiles include
`npm:@signalridge/pi-goal`, which provides the session-scoped `/goal` command and
`goal_complete`, `goal_blocked`, and `goal_wait` tools for autonomous, verifiable
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
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The `pi-goal` package is included in both settings profiles; use `/goal` to start or manage a session-scoped autonomous goal. The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
