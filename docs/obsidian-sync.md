# Obsidian vault sync

The vaults are ordinary files and directories. Obsidian is only the editor;
it is not the synchronization mechanism. The supported setup is **Syncthing**
with the always-on Oracle host as the hub and a complete local copy on each
personal device.

This guide is for adding a new personal macOS workstation, including the EPFL
Apple Silicon MacBook Pro, to the existing setup.

## Layout and invariants

- The hub's Syncthing folder is `/home/ubuntu/vaults/`.
- On a workstation, use `~/vaults/` as the local Syncthing destination unless
  the user explicitly chooses another path.
- The current vaults are `personal` and `work`, so open these folders in
  Obsidian:
  `~/vaults/personal` and `~/vaults/work`.
- Keep `.obsidian` directories: they contain vault configuration that is part
  of the working setup.
- `.stfolder` is Syncthing metadata. Never remove it manually.
- The hub and vault directories also contain Git metadata. Do not clone the
  vaults separately, run `git init`, or use Git/rsync as a replacement for
  Syncthing. Do not remove `.git` directories while preparing the workstation.
- Do not enable Obsidian Sync for these vaults. Running two synchronization
  systems against the same files is unsupported.

Syncthing is bidirectional. The hub is not a backup; maintain separate backups
before destructive cleanup or conflict resolution.

## Agent safety rules

An agent setting up a new workstation may install Syncthing and Obsidian after
confirming that this is the intended personal Mac, but it must:

1. Read this guide completely and identify the machine as **Personal macOS**.
2. Check for an existing `~/vaults` directory before changing anything. If it
   contains files, do not overwrite, delete, or merge it automatically; stop
   and ask the user whether it is an existing vault or a backup to preserve.
3. Confirm that SSH access to the hub works before changing Syncthing settings.
4. Pair devices and share the existing hub folder through the Syncthing GUI.
   Do not create a second hub folder or change the hub's folder path.
5. Never print, copy, or request private keys, Syncthing database files, API
   keys, or passwords. Device IDs are safe to enter in the Syncthing GUI but
   should not be committed to this repository.
6. Do not expose either Syncthing GUI to the network. The GUI should remain
   bound to `127.0.0.1`; only the Syncthing data listener needs to connect.
7. Do not open Obsidian until Syncthing reports that the initial transfer is
   complete, or until the user explicitly accepts working during the transfer.

## Install on Apple Silicon macOS

Retain existing installations. If Homebrew is available, install the native
packages:

```sh
brew install syncthing
brew install --cask obsidian
```

If Homebrew is not installed, use the official Syncthing and Obsidian downloads
instead; do not install an Intel binary under Rosetta when an Apple Silicon
build is available. The package manager and application source may be changed
by local policy, but the Syncthing folder and pairing procedure below remain
the same.

Start Syncthing as the logged-in user and confirm that it is running:

```sh
brew services start syncthing
brew services list | grep syncthing
open http://127.0.0.1:8384
```

The first visit may ask for a GUI username and password. Set them if prompted;
do not reuse an account password. Leave the GUI bound to loopback.

## Confirm SSH access to the hub

The tracked SSH configuration does not define the private `oracle` alias; it
is a local workstation prerequisite. The user must provide that alias and its
private key out of band, or use an existing equivalent host alias. Do not put
private-key material or the server address in this repository.

Verify connectivity without exposing credentials:

```sh
ssh oracle true
```

If the alias is unavailable, stop and ask the user to configure it. Do not
invent a host name, generate a replacement key, or alter the hub's SSH
configuration from this guide.

The hub's Syncthing GUI is loopback-only. To inspect it from the Mac without
colliding with the Mac's local GUI, use a different local port:

```sh
ssh -N -L 18384:127.0.0.1:8384 oracle
```

Keep that SSH process running and open <http://127.0.0.1:18384>. Use the
hub's Syncthing GUI only for pairing and sharing the existing folder. The hub
service lifecycle and its private configuration belong to the hub's local
administration documentation.

## Pair the Mac and share the existing folder

Perform this in the two Syncthing GUIs. The exact labels vary slightly by
Syncthing version.

1. In the Mac GUI, copy the Mac's **Device ID**.
2. In the hub GUI at port `18384`, add a remote device with that Device ID and
   a recognizable name such as `epfl-m1-macbook-pro`. Save it.
3. In the Mac GUI, add/accept the hub as a remote device using the hub's Device
   ID shown by the hub GUI. Accept the device on both sides if prompted.
4. In the hub GUI, open the existing folder whose path is
   `/home/ubuntu/vaults/`. Share that existing folder with the new Mac device.
   Do not add another folder pointing at the same path.
5. In the Mac GUI, accept the shared folder and set its local path to
   `~/vaults`. If the GUI asks whether to create the directory, approve it
   only when the preflight check confirmed that it is absent or empty.
6. Wait for the initial scan and transfer. The folder should eventually show
   **Up to Date** on the Mac and on the hub.

If Syncthing reports a folder ID or path conflict, stop rather than accepting
an automatic rename or deleting a folder. There must be one shared folder
containing both `personal` and `work`.

## Configure Obsidian

After the first sync is complete, launch Obsidian and open existing folders;
do not create new vaults over them:

- `~/vaults/personal`
- `~/vaults/work`

Keep Obsidian's normal file-based vault mode. Do not enable Obsidian Sync,
third-party sync plugins, iCloud storage for these folders, or an additional
rsync job. Obsidian can be open on both machines, but simultaneous edits to the
same note can produce Syncthing conflict copies; resolve those manually and
preserve the user's content.

## Verification

Run the following on the Mac:

```sh
brew services list | grep syncthing
find "$HOME/vaults" -maxdepth 2 -name .stfolder -print
find "$HOME/vaults" -maxdepth 2 -type d \( -name personal -o -name work \) -print
```

Then verify in the Syncthing GUI that the shared folder is **Up to Date** and
that the hub device is connected. Verify in Obsidian that both existing vaults
open and that their `.obsidian` settings are present.

For an end-to-end test, only with the user's approval, create a uniquely named
small Markdown file in one vault on the Mac, wait for it to appear on the hub,
then remove it from the same machine and wait for the deletion to propagate.
Do not use a real note for this test.

## Troubleshooting

- **Hub device is disconnected:** verify `ssh oracle true`, network/VPN
  access, and the device IDs in both GUIs. Do not change discovery, relay, or
  firewall settings as a first step.
- **Folder is not offered on the Mac:** share the existing hub folder with the
  Mac device; do not create a new folder on either side.
- **Initial sync is slow:** keep both Syncthing services running and inspect
  the GUI's folder and device status. Do not interrupt it by opening, moving,
  or deleting the destination folder.
- **Conflict files appear:** stop editing the affected note, compare the
  original and conflict copy, preserve the desired content, and remove only
  the resolved conflict copy after checking both devices.
- **A local vault already exists:** stop. Back it up and compare it with the
  hub before choosing whether to use it as the Syncthing destination.

## Removal

To remove only the Mac from synchronization, first stop using the vaults in
Obsidian, then remove the Mac device and its shared-folder membership in both
Syncthing GUIs. Stop the local service if desired:

```sh
brew services stop syncthing
```

Do not delete `~/vaults` automatically, and never delete the hub's
`/home/ubuntu/vaults/` folder as part of workstation removal.
