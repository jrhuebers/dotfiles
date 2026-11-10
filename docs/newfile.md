# NewFile for macOS Finder

[NewFile](https://github.com/mariusgm/newfile) is an optional macOS GUI utility
that adds file creation to Finder's context menu and toolbar through a sandboxed
Finder Sync extension. It is not needed on headless or Linux hosts.

## Install

Use the project's official Homebrew tap (macOS Ventura 13 or newer):

```sh
brew install --cask mariusgm/newfile/newfile
open -a NewFile
```

Homebrew installs `/Applications/NewFile.app`. Launch it once to register its
embedded extension, then enable NewFile in **System Settings → General → Login
Items & Extensions**. On macOS 15, look under **Added Extensions**; the location
may vary on later releases (see upstream instructions). Enable it interactively;
do not bypass macOS extension approval or managed-device policy.

In Finder, use **View → Customize Toolbar…** to add the NewFile button. The
right-click menu creates a file in the current folder; conflicting names are
incremented rather than overwritten. For iCloud Drive folders, upstream
recommends the toolbar button because Finder may suppress third-party context
menus there.

Open NewFile's preferences with **⌘,** to choose file types, default filenames,
and starter templates. No shell configuration or repository symlinks are needed.

## Verification and updates

```sh
brew list --cask --versions newfile
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' /Applications/NewFile.app/Contents/Info.plist
codesign --verify --deep --strict /Applications/NewFile.app
spctl --assess --type execute --verbose=2 /Applications/NewFile.app
```

After enabling the extension, test file creation in a disposable local folder.
Check both the toolbar and context menu. NewFile supports Sparkle in-app updates;
the Homebrew-managed installation can also be updated with
`brew upgrade --cask mariusgm/newfile/newfile`.

## Removal

Quit NewFile and disable its extension in System Settings first (the extension
can remain active after quitting the app). Then:

```sh
brew uninstall --cask newfile
```

Do not use `--zap` unless deleting saved file types/templates is explicitly
wanted. Preserve NewFile's containers and group-container data by default.
Uninstalling the app does not remove files previously created with it. The
`mariusgm/newfile` tap can optionally be removed with
`brew untap mariusgm/newfile` once unused.
