# VS Code Finder Quick Action

A native macOS Automator Quick Action opens selected Finder folders in Visual
Studio Code. No third-party Finder extension, shell action, or administrator
access is required. This is macOS-only, not a Linux or cluster configuration.

## Prerequisites and source

Install VS Code at `/Applications/Visual Studio Code.app`. For example, on a
Homebrew-managed personal Mac:

```sh
brew install --cask visual-studio-code
```

The repository source is `Open in VS Code.workflow/`. Its `Contents/Info.plist`
registers **Open in VS Code** for `public.folder` in Finder. Its
`Contents/document.wflow` uses Apple's **Open Finder Items** action with the
application path above. The `code` CLI is not required. If VS Code is installed
elsewhere, open the installed workflow in Automator and change **Open with**.

## Installation

From the repository root, copy the workflow into the user's Services directory.
The guard refuses to overwrite an existing workflow; back up and inspect an
existing copy before deliberately replacing it.

```sh
mkdir -p "$HOME/Library/Services"
if [ ! -e "$HOME/Library/Services/Open in VS Code.workflow" ]; then
  cp -R "Open in VS Code.workflow" "$HOME/Library/Services/"
else
  printf '%s\n' 'Already installed; inspect/back up before replacing.'
fi
/System/Library/CoreServices/pbs -update
```

The installed destination is
`~/Library/Services/Open in VS Code.workflow`. It is a copy, so subsequent
repository changes do not automatically change the installed action.

Right-click a folder in Finder and choose **Quick Actions → Open in VS Code**
or **Services → Open in VS Code**, depending on the macOS menu layout.

### Important: registered but missing from both menus

Copying a workflow and running `pbs -update` can register it without enabling
its menu presentation. This occurred on macOS 15.8.1: both menus lacked the
action even though `pbs -read_bundle` listed it. Explicitly enabling its
presentation modes, then flushing/updating the cache, fixed it; the user
confirmed that opening a folder works.

First try **System Settings → Keyboard → Keyboard Shortcuts → Services** and
enable **Open in VS Code** under **Files and Folders**. The Finder **Customize…**
button may instead open app-extension settings, which is not the legacy
Automator Services configuration.

For a reproducible command-line fix, back up the current Services preferences:

```sh
backup="$HOME/admin-docs/backups/vscode-finder-service-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
defaults export pbs "$backup/pbs.plist"
```

Then enable only this service's presentation modes. This preserves other
services, shortcuts, and preferences. The `(null)` prefix is intentional: this
workflow has no application bundle identifier in its service registration.

```sh
/usr/bin/osascript -l JavaScript <<'JS'
ObjC.import('Foundation');
const prefs = $.NSUserDefaults.alloc.initWithSuiteName('pbs');
const old = prefs.dictionaryForKey('NSServicesStatus');
const status = old.isNil() ? {} : ObjC.deepUnwrap(old);
const key = '(null) - Open in VS Code - runWorkflowAsService';
const entry = status[key] || {};
entry.presentation_modes = Object.assign({}, entry.presentation_modes || {}, {
  ContextMenu: true, FinderPreview: true, ServicesMenu: true, TouchBar: true
});
status[key] = entry;
prefs.setObjectForKey($(status), 'NSServicesStatus');
prefs.synchronize;
JS
/System/Library/CoreServices/pbs -flush
/System/Library/CoreServices/pbs -update
```

Close and reopen the context menu, then try again. If necessary, relaunch Finder
after any Finder file operations finish; a reboot should not normally be needed.

## Verification

```sh
plutil -lint \
  "$HOME/Library/Services/Open in VS Code.workflow/Contents/Info.plist" \
  "$HOME/Library/Services/Open in VS Code.workflow/Contents/document.wflow"
/System/Library/CoreServices/pbs -read_bundle \
  "$HOME/Library/Services/Open in VS Code.workflow"
defaults read pbs NSServicesStatus
```

The service registration should show **Open in VS Code**, `public.folder`, and
`com.apple.finder`. If the command-line visibility fix was applied, its
`presentation_modes` should be enabled. Finally, right-click a test folder and
invoke the action; VS Code should open that folder. Registration alone does
not prove the item is visible or executable in Finder.

To assign an optional keyboard shortcut, use **System Settings → Keyboard →
Keyboard Shortcuts → Services**.

## Removal

Remove only this workflow, not the Services directory or other actions:

```sh
rm -rf "$HOME/Library/Services/Open in VS Code.workflow"
```

If the explicit visibility entry was added, remove only that preference entry:

```sh
/usr/bin/osascript -l JavaScript <<'JS'
ObjC.import('Foundation');
const prefs = $.NSUserDefaults.alloc.initWithSuiteName('pbs');
const old = prefs.dictionaryForKey('NSServicesStatus');
if (!old.isNil()) {
  const status = ObjC.deepUnwrap(old);
  delete status['(null) - Open in VS Code - runWorkflowAsService'];
  prefs.setObjectForKey($(status), 'NSServicesStatus');
  prefs.synchronize;
}
JS
/System/Library/CoreServices/pbs -flush
/System/Library/CoreServices/pbs -update
```

Do not restore the entire preferences backup over newer unrelated changes.
Removal does not uninstall VS Code or change its settings or project files.
