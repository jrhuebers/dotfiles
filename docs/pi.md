# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps separate settings profiles because a compute cluster has Slurm tools that
should not be enabled on personal machines:

- `pi/cluster/settings.json` → `~/.pi/agent/settings.json` on a cluster host.
- `pi/personal/settings.json` → `~/.pi/agent/settings.json` on a laptop,
  desktop PC, or personal server such as the Oracle server.
- `pi/models.json` is shared by both profiles.

The profile difference is currently one package: `git:github.com/jrhuebers/pi-slurm`
is enabled only in the cluster profile. All other Pi settings and packages are
currently identical, including `npm:pi-simple-web-tools@0.1.0`. The web-tools
credential is user-local and secret-bearing; follow
[`pi-simple-web-tools.md`](pi-simple-web-tools.md) rather than tracking it here.
See [`device-profiles.md`](device-profiles.md) for the complete cluster/personal
split across this repository.

## Refresh the repository copies

Set `PI_PROFILE` to the profile used by the live machine before refreshing:

```sh
PI_PROFILE=personal  # use cluster on a cluster host
mkdir -p ~/dotfiles/pi/$PI_PROFILE
cp -p ~/.pi/agent/settings.json ~/dotfiles/pi/$PI_PROFILE/settings.json
cp -p ~/.pi/agent/models.json ~/dotfiles/pi/models.json
```

## Deploy the repository copies

From a checkout at `~/dotfiles`, select exactly one profile:

```sh
PI_PROFILE=personal  # use cluster on a cluster host
case "$PI_PROFILE" in cluster|personal) ;; *) exit 2 ;; esac
mkdir -p ~/.pi/agent
cp -p ~/dotfiles/pi/$PI_PROFILE/settings.json ~/.pi/agent/settings.json
cp -p ~/dotfiles/pi/models.json ~/.pi/agent/models.json
```

Do not install the cluster profile on a personal device: it registers Slurm
commands that are unavailable or inappropriate there. Restart Pi after
configuration changes so it reloads the files. Verify the selected profile with:

```sh
cmp -s ~/dotfiles/pi/$PI_PROFILE/settings.json ~/.pi/agent/settings.json && \
  cmp -s ~/dotfiles/pi/models.json ~/.pi/agent/models.json && \
  echo "Pi $PI_PROFILE configuration copies match."
```

Do not add authentication tokens or other secrets to the tracked configuration.

To install or remove a package in the live global Pi setup:

```sh
pi install npm:pi-btw
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
