# Pi agent

Pi's user-level configuration is installed under `~/.pi/agent`. This repository
keeps the two configuration files that are currently used on the server:

- `pi/settings.json` → `~/.pi/agent/settings.json`
- `pi/models.json` → `~/.pi/agent/models.json`

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
