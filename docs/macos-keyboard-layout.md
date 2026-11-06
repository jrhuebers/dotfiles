# macOS keyboard layout: ABC - Umlauts

A standalone macOS layout based on the built-in **ABC** layout, with only
these changes:

| Shortcut | Output | With Shift or Caps Lock |
| --- | --- | --- |
| Option+A | ä | Ä |
| Option+O | ö | Ö |
| Option+U | ü | Ü |

Both left and right Option/Shift keys work. Overrides apply only without
Command or Control, so those shortcuts remain identical to ABC. Other
Option symbols and remaining dead keys are preserved. Option+U directly
produces ü instead of starting ABC's diaeresis dead key; this is an intended
consequence of the requested change. A pending unrelated accent terminates
normally before a direct umlaut is emitted.

This is macOS-only and optional for the **Personal macOS** profile. Do not
deploy it to Linux or cluster hosts; the Linux layout is documented separately
in [`linux-keyboard-layout.md`](linux-keyboard-layout.md).

## Repository files

All files are under `macos/keyboard-layouts/abc-umlauts/`:

- `ABC - Umlauts.keylayout`: complete installable XML layout, including ABC's
  hardware variants, modifier tables, character sequences, dead-key actions,
  and state terminators. This is the only file needed for installation.
- `native.py`: reads the installed ABC Unicode tables using public Carbon and
  Core Foundation APIs, exporting a local `ABC.uchr` snapshot for regeneration.
- `build.py`: converts that snapshot to XML and adds the three letter overrides.
- `validate.py`: asks macOS to compile/register the installed custom layout,
  then compares native keyboard translations against the machine's built-in ABC.
  It does not enable or select the layout.
- `.gitignore`: excludes generated binary snapshots and Python caches.

The tracked layout was generated from macOS 15.8.1's actual ABC layout on Apple
Silicon. It is a standalone snapshot, not a dynamic inheritance of future ABC
updates. On a different macOS version, run the validator; regenerate and review
if the system's ABC differs. The tools use Python 3's standard library only;
no Python packages, layout editor, or compiler are required. Python is optional
for installation but required for regeneration and automated verification.

## Installation

No sudo or system-wide changes are needed. Install a **copy**, not a symlink,
so macOS has a regular layout file independent of repository moves.

From a checkout at `~/dotfiles`:

```sh
(
  set -eu
  source="$HOME/dotfiles/macos/keyboard-layouts/abc-umlauts/ABC - Umlauts.keylayout"
  destination="$HOME/Library/Keyboard Layouts/ABC - Umlauts.keylayout"
  mkdir -p "$HOME/Library/Keyboard Layouts"
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    backup="$HOME/admin-docs/backups/keyboard-layouts/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup"
    cp -p "$destination" "$backup/ABC - Umlauts.keylayout"
    printf 'Previous layout backed up to %s\n' "$backup"
  fi
  cp "$source" "$destination"
)
```

Then open **System Settings → Keyboard → Text Input → Edit → +**. Find
**ABC - Umlauts** (usually under English or Others), add it, and select it
from the input menu. Retain ABC as a fallback. If it does not appear, save
work and log out/back in. Do not kill applications or disrupt live sessions
merely to refresh the input-source list.

Installing the file alone does not switch the active input source or remove
ABC. No MDM, security settings, system layouts, or input-source preferences
need to be modified by scripts.

## Verification

With the layout file installed, run:

```sh
python3 ~/dotfiles/macos/keyboard-layouts/abc-umlauts/validate.py
```

The validator calls `TISRegisterInputSource` to make the file available and
retrieve macOS's compiled Unicode layout. It compares `UCKeyTranslate` output
and next state for 15 representative hardware types, all 256 modifier masks,
all 128 key codes, and ABC's initial plus five dead-key states. It fails on
any unexpected difference and checks the umlaut overrides explicitly.

On the baseline macOS version, the result is **2,949,120 comparisons, zero
unexpected differences**. The 6,480 differing cases are the requested keys
with their modifier/hardware/pending-accent variants. macOS may print an
internal keyboard-ID collision/renumbering warning during registration;
that does not change the mappings or display name.

After activation, also test manually in TextEdit:

- Option+A/O/U → ä/ö/ü; Shift+Option+A/O/U → Ä/Ö/Ü.
- Option+E then E → é; Option+N then N → ñ.
- Ordinary typing, punctuation, and your usual Command/Control shortcuts.

## Regenerate against the current system ABC

Regeneration is optional. It changes the repository layout file, not the
installed copy. Start with a clean working tree for these files, then:

```sh
cd ~/dotfiles/macos/keyboard-layouts/abc-umlauts
python3 native.py
python3 build.py
git diff -- 'ABC - Umlauts.keylayout'
```

The binary `ABC.uchr` is generated locally and ignored by Git. The generator
expects ABC's known eight-table structure and shared modifier/state tables;
it stops rather than silently converting an unsupported structure. Review
the diff, install the new copy with the backed-up procedure above, and rerun
`validate.py` before committing an update.

## Removal and rollback

1. Switch to ABC in the input menu.
2. Remove ABC - Umlauts from the input-source list in System Settings.
3. Remove only the installed custom file:

   ```sh
   rm -i "$HOME/Library/Keyboard Layouts/ABC - Umlauts.keylayout"
   ```

4. If replacing a pre-existing version, restore only that file from the backup
   printed during installation. Log out/in if macOS caches the old layout.

Do not remove the Keyboard Layouts directory or alter Apple's built-in ABC.

## Format reference

Apple's [Installable Keyboard Layouts (TN2056)](https://developer.apple.com/library/archive/technotes/tn2056/_index.html)
describes installation, hardware mappings, modifier selection, actions, and
terminators. Numeric entities for control characters are intentional in this
format; generic strict XML parsers are not a substitute for macOS's layout
compiler and native translation tests.
