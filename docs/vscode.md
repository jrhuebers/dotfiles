# VS Code settings

`VSCode/settings.json` is a personal GUI workstation configuration. It is off
for cluster hosts and headless servers; a local workstation may still use VS
Code to connect to a remote cluster. Select the machine profile first in
[`device-profiles.md`](device-profiles.md).

## Deploy

Install VS Code through the platform's supported distribution first. Then copy
the tracked JSON-with-comments settings file to VS Code's user-settings path:

```sh
# Linux
mkdir -p ~/.config/Code/User
cp -p ~/dotfiles/VSCode/settings.json ~/.config/Code/User/settings.json

# macOS
mkdir -p "$HOME/Library/Application Support/Code/User"
cp -p ~/dotfiles/VSCode/settings.json \
  "$HOME/Library/Application Support/Code/User/settings.json"
```

The settings configure editor appearance, Python formatting/type checking,
file exclusions, and agent UI behavior. They do not install extensions such as
Ruff or the Python extension; install the extensions required by the projects
being edited.

## Verify and remove

Restart VS Code, then open **Preferences: Open User Settings (JSON)** and
confirm that the selected user-settings file contains the tracked values. To
remove this configuration, restore a backup or delete the installed
`settings.json`; this does not uninstall VS Code or its extensions.
