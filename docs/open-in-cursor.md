# Cursor Finder service

The `Open in Cursor.workflow` directory provides a macOS Finder service for opening files or folders in Cursor.

## Installation

From the repository root, copy or symlink the workflow into the user Services directory:

```sh
mkdir -p ~/Library/Services
cp -R "Open in Cursor.workflow" ~/Library/Services/
```

Alternatively, use a symlink to keep the installed service backed by this repository:

```sh
mkdir -p ~/Library/Services
ln -s "$PWD/Open in Cursor.workflow" ~/Library/Services/
```

The source is `Open in Cursor.workflow` in this repository; the installed destination is `~/Library/Services/Open in Cursor.workflow`.

## Verification

In Finder, right-click a file or folder and choose **Quick Actions → Open in Cursor** (or the corresponding Services entry).

## Removal

```sh
rm -rf "$HOME/Library/Services/Open in Cursor.workflow"
```

