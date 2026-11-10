# macOS Finder defaults

These preferences apply to the logged-in macOS GUI user, not to Linux or
cluster hosts. They affect new Finder windows, not the locations of windows
already open or restored from a previous session.

## Open new windows at the home folder

In **Finder → Settings → General**, set **New Finder windows show** to your
home folder (for example, **huebers**) instead of **Recents**.

Equivalent user-local commands:

```sh
defaults write com.apple.finder NewWindowTarget -string PfHm
defaults write com.apple.finder NewWindowTargetPath -string \
  "$(/usr/bin/python3 -c 'from pathlib import Path; print(Path.home().as_uri() + "/")')"
```

`PfHm` selects the home folder. The path command generates a correctly escaped
file URL for the current user rather than hard-coding a username. It requires
Python 3; the Finder Settings UI does not.

Before changing an existing configuration, record whether each key exists and
its value:

```sh
defaults read com.apple.finder NewWindowTarget
defaults read com.apple.finder NewWindowTargetPath
```

A missing-key error means the key has no explicit value; record that absence
rather than inventing a previous path. Keep machine-specific backups under
`~/admin-docs/backups/`, outside the repository.

## Verify and apply

```sh
defaults read com.apple.finder NewWindowTarget
defaults read com.apple.finder NewWindowTargetPath
```

Expect `PfHm` and a URL such as `file:///Users/huebers/`. In Finder, press
**Command+N** and confirm the new window opens the home folder. Clicking Finder
in the Dock can reactivate an existing window instead of creating a new one.

If Finder continues to use the old preference, relaunch it after file operations
finish: hold **Option**, right-click Finder in the Dock, and select **Relaunch**.
Do not relaunch Finder while it is performing important copy/move operations.
There is no need to close existing windows merely to write the preference.

## Restore Recents or the prior configuration

To choose Recents again, use Finder Settings, or:

```sh
defaults write com.apple.finder NewWindowTarget -string PfAF
```

For an exact rollback, restore each recorded value. If a key was originally
absent, delete only that key with `defaults delete com.apple.finder KEY` rather
than clearing the entire Finder preference domain. The home URL is not used
while `PfAF` (Recents) is selected. Relaunch Finder only if necessary, after
file operations finish.

## Related Finder integrations

- [Open folders in VS Code](open-in-vscode.md)
- [Open files and folders in Cursor](open-in-cursor.md)
- [NewFile Finder file-creation extension](newfile.md)
