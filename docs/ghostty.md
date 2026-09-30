# Ghostty

Ghostty is an optional GUI workstation terminal. Do not deploy it on headless
servers or cluster hosts. On macOS install the official app from
<https://ghostty.org/download> or use `brew install --cask ghostty` if allowed
by local policy. Retain an existing installation rather than reinstalling.

## Configuration

The tracked source is `.config/ghostty/config`. It selects the light
`TokyoNight Day` theme, light window decorations, and a non-blinking cursor.

Deploy as a symlink after backing up any pre-existing configuration:

```sh
mkdir -p ~/.config/ghostty
ln -s ~/dotfiles/.config/ghostty/config ~/.config/ghostty/config
```

Do not overwrite unrelated files. On macOS also inspect
`~/Library/Application Support/com.mitchellh.ghostty/` for an existing native
configuration; avoid conflicting settings in the two supported locations.

Reload with Ghostty's **Reload Configuration** menu action (normally
Cmd+Shift+,), or quit and reopen the app. Setting Ghostty as the preferred
terminal for specific tools is separate; this deployment does not change
macOS file associations or other applications' terminal preferences.

`cursor-style-blink = false` sets the terminal default. Programs such as Vim
may still override blinking using DECSCUSR escape sequences; configure the
application too if its cursor continues to blink.

## Verification

Ghostty 1.3.1 on Apple Silicon macOS accepted and loaded all three settings:

```sh
/Applications/Ghostty.app/Contents/MacOS/ghostty +validate-config
/Applications/Ghostty.app/Contents/MacOS/ghostty +show-config
```

Verify the effective `theme`, `window-theme`, and `cursor-style-blink` values,
then check the visual appearance in a new terminal window.

## Removal

Remove only the deployed symlink and restore any prior configuration backup.
Remove a Homebrew-managed app with `brew uninstall --cask ghostty`; for a
manually installed app use macOS's normal application-removal procedure.
Do not delete session state or unrelated application settings automatically.
