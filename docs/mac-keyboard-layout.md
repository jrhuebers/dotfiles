# macOS US International keyboard layout (no dead keys)

This guide installs WillerWasTaken's **US International AltGr no dead key**
layout for the current user, without `sudo` or a system-wide file change. It is
separate from the user-level Linux XKB layout in
[`linux-keyboard-layout.md`](linux-keyboard-layout.md).

## Install

The upstream repository's README copies the `.keylayout` file into
`/Library/Keyboard Layouts` and calls for a reboot. On a managed workstation,
prefer the per-user location instead:

```sh
mkdir -p "$HOME/Library/Keyboard Layouts"
cp "Us intl altgr no dead key.bundle/Contents/Resources/Us no dead key.keylayout" \
  "$HOME/Library/Keyboard Layouts/Us no dead key.keylayout"
```

Run the copy command from a clone of
<https://github.com/WillerWasTaken/mac-us-int-no-dead-key>. Do not replace an
existing file without backing it up first. The upstream bundle also contains
metadata and an icon; its README specifically installs only the `.keylayout`
file.

After installation, log out and back in if macOS does not discover the layout
immediately. Open **System Settings → Keyboard → Text Input → Edit**, add
**Us no dead key** (it may appear under Other), and select it as the active
input source. Adding the file does not change the active input source by itself.

## Verify and remove

Confirm the installed file exists and matches the source. Then verify the
layout appears in the input-source picker and test the intended Option/AltGr
characters in a text editor. The upstream file uses XML 1.1 character
references, so XML parsers that only accept XML 1.0 may reject it; that alone
is not evidence that macOS cannot load the layout.

Remove only the installed user-level file to uninstall:

```sh
rm "$HOME/Library/Keyboard Layouts/Us no dead key.keylayout"
```

Then remove that input source from System Settings. No reboot, `sudo`, or
changes to `/Library/Keyboard Layouts` are required for removal.

## Upstream

- Project: <https://github.com/WillerWasTaken/mac-us-int-no-dead-key>
- Upstream README installation and reboot guidance: follow its documented
  system-wide instructions only when specifically appropriate; this guide uses
  the user Library instead.
