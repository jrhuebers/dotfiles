# GNOME keyboard layout

This repository provides a small user-level XKB layout for GNOME on Wayland.
It keeps the standard British (`gb`) layout and adds these level-3 mappings:

| Shortcut | Character |
| --- | --- |
| `AltGr` + `U` | `ü` |
| `AltGr` + `A` | `ä` |
| `AltGr` + `O` | `ö` |
| `AltGr` + `S` | `ß` |

Holding `Shift` as well produces `Ü`, `Ä`, `Ö`, and `ẞ`.

## Files and responsibilities

- `.config/xkb/symbols/custom` contains the XKB symbols. It includes the
  system British layout with `include "gb(basic)"` and overrides only the four
  letter keys.
- `~/.config/xkb/symbols/custom` is the installed user copy or symlink of that
  file. GNOME's Wayland stack uses `libxkbcommon`, which searches user XKB
  configuration paths before the system layout database.
- GNOME stores the selected input sources in dconf, exposed through
  `org.gnome.desktop.input-sources`. The `sources` value selects the layouts;
  `current` selects the zero-based active source.

The layout is named `custom` because `xkeyboard-config` already registers that
layout name for user-defined layouts. This lets GNOME accept it without
modifying `/usr/share/X11/xkb` or adding a system package file.

## Installation

From a checkout at `~/dotfiles`, create the user XKB directory and link the
symbols file:

```bash
mkdir -p ~/.config/xkb/symbols
ln -sfn ~/dotfiles/.config/xkb/symbols/custom ~/.config/xkb/symbols/custom
```

Then select the custom layout as the only GNOME input source:

```bash
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'custom')]"
gsettings set org.gnome.desktop.input-sources current 0
```

If GNOME does not reload the symbols immediately, log out and back in. Test
the shortcuts in a native Wayland application, such as GNOME Text Editor.

## Notes

`.Xmodmap` and `setxkbmap` are not the persistent configuration mechanism for
native Wayland applications. `.Xmodmap` may affect X11 sessions, while
`setxkbmap` primarily affects X11/XWayland; the persistent GNOME setting is the
dconf input-source selection above.

Do not edit the vendor files under `/usr/share/X11/xkb`; package updates may
overwrite them. The user layout is supported by
[`libxkbcommon`](https://github.com/xkbcommon/libxkbcommon/blob/master/doc/compatibility.md)
and the GNOME input-source setting is documented in the
[GNOME keyboard-layout help](https://help.gnome.org/users/gnome-help/stable/keyboard-layouts.html).
