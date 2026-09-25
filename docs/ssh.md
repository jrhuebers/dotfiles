# SSH client configuration

`.ssh/config` is a **personal client-side** configuration for reaching remote
machines. It is not a configuration to deploy on a cluster login or compute
host. Check [`device-profiles.md`](device-profiles.md) before using it.

## Deploy

Back up a pre-existing local configuration, then copy the tracked file with
restricted permissions:

```sh
mkdir -p ~/.ssh
chmod 700 ~/.ssh
[ ! -e ~/.ssh/config ] || cp -p ~/.ssh/config ~/.ssh/config.bak
install -m 600 ~/dotfiles/.ssh/config ~/.ssh/config
```

The file may name a private key, but private keys themselves are deliberately
not tracked. Ensure that every referenced key exists locally with restrictive
permissions before connecting.

The tracked configuration includes aliases for the LTS2 lab frontend:

```sshconfig
Host lts2
    HostName stivm0163.xaas.epfl.ch
    User huebers
    IdentityFile ~/.ssh/id_ed25519

Host lts2-via-oracle
    HostName stivm0163.xaas.epfl.ch
    User huebers
    IdentityFile ~/.ssh/id_ed25519
    ProxyCommand ssh oracle -W 127.0.0.1:2222
```

`lts2` is for direct access when the frontend is reachable. `lts2-via-oracle`
requires the `oracle` SSH alias and the LTS2-to-Oracle reverse tunnel described
in the local administration documentation. The tracked `rcp` alias is for a
separate RCP cluster and must not be used for LTS2:

```sshconfig
Host rcp
    HostName jumphost.rcp.epfl.ch
    User huebers
    IdentityFile ~/.ssh/id_ed25519
```

## Verify

For an alias already present in the configuration, inspect the resolved
non-secret client settings and then connect normally:

```sh
ssh -G <configured-alias>
ssh <configured-alias>
```

Do not print or commit private keys, authentication agents, passwords, or host
credentials.

## Removal

Restore `~/.ssh/config.bak` if it was created, or remove the deployed
`~/.ssh/config` only when it is no longer needed.
