# Task: GNOME custom keyboard layout

- [x] Pull the latest `origin/main` before making changes.
- [x] Add the British XKB layout with German characters on AltGr.
- [x] Document the GNOME/Wayland XKB and dconf configuration.
- [x] Remove the German input source from the active GNOME settings.
- [x] Verify the XKB symbols compile and the GNOME source is `custom`.

Validation:

- `git pull --ff-only`
- `xkbcomp` compilation with the repository `.config/xkb` include path
- `gsettings get org.gnome.desktop.input-sources sources` → `[('xkb', 'custom')]`
