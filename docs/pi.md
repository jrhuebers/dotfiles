# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps the two configuration files that are currently used on the server:

- `pi/settings.json` → `~/.pi/agent/settings.json`
- `pi/models.json` → `~/.pi/agent/models.json`

The global package list includes `npm:pi-btw`, which provides the `/btw` side-conversation extension, and `npm:pi-simple-web-tools@0.1.0`, which provides compact `web_search` and `fetch_content` tools. Their source specs are recorded in `pi/settings.json`; Pi installs them under `~/.pi/agent/npm/node_modules/`. The simple web-tools Exa credential is user-local and secret-bearing; follow [`pi-simple-web-tools.md`](pi-simple-web-tools.md) rather than tracking it here.

## Refresh the repository copies

After changing the live Pi configuration, refresh the repository snapshots from
`~/dotfiles`:

```sh
mkdir -p ~/dotfiles/pi
cp -p ~/.pi/agent/{settings.json,models.json} ~/dotfiles/pi/
```

## Deploy the repository copies

From a checkout at `~/dotfiles`, install the tracked configuration files with:

```sh
mkdir -p ~/.pi/agent
cp -p ~/dotfiles/pi/{settings.json,models.json} ~/.pi/agent/
```

Restart Pi after configuration changes so it reloads the files. Verify that the
repository and installed copies match with:

```sh
cmp -s ~/dotfiles/pi/settings.json ~/.pi/agent/settings.json && \
  cmp -s ~/dotfiles/pi/models.json ~/.pi/agent/models.json && \
  echo 'Pi configuration copies match.'
```

Do not add authentication tokens or other secrets to the tracked configuration.

To install or remove the package in the live global Pi setup:

```sh
pi install npm:pi-btw
pi remove npm:pi-btw
```

After installation, verify it with `pi list` and restart Pi so the extension loads. The extension's `/btw` thread can use the configured Pi model and coding tools; review third-party package source before updating it.
