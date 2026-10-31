# VS Code settings

`VSCode/settings.json` is a personal GUI workstation configuration. It is off
for cluster hosts and headless servers; a local workstation may still use VS
Code to connect to a remote cluster. Select the machine profile first in
[`device-profiles.md`](device-profiles.md).

## Deploy

Install VS Code through the platform's supported distribution first. Back up
existing user settings before replacement; merge rather than overwrite if local
customizations must be retained. Then copy the tracked JSON-with-comments
settings file to VS Code's user-settings path:

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

## LaTeX editing and formatting

For LaTeX work, install the extension separately:

```sh
code --install-extension James-Yu.latex-workshop
```

Install and verify `latexindent`, deploy its shared style, and configure its
native user settings using [`latexindent.md`](latexindent.md). The shared style
is required for the global formatting behavior in projects without local YAML.
The tracked settings use the portable executable name `latexindent`. On a Mac
where MacTeX's executable shadows Homebrew's working copy, set the installed
user setting `latex-workshop.formatting.latexindent.path` to the absolute
Homebrew path described in that guide. Do not overwrite this host-specific
path when refreshing settings from the repository.

The shared defaults for both `latex` and `tex` language modes are:

- Visual word wrapping on, without inserting source line breaks.
- LaTeX Workshop as the formatter, with two-space indentation.
- Format-on-save explicitly off; Python's separate Ruff settings are unchanged.
- Global formatter arguments `-m`, `-rv`, `-l=%DIR%/latexindent.yaml`, `-c`,
  `%DIR%/build/`, and `%TMPFILE%`. Persistent formatter logs go into `build/`.
- A shared native user profile supplies prose unwrapping, compact source-list
  layout, and single-line `$$ ... $$` displays except when explicit `\\` row
  breaks start each following equation row on a new source line. Optional project YAML overlays
  that style; missing project YAML is nonfatal. Formatting is still manual.
- Global LaTeX Workshop output and auxiliary directories point into `build/`.
- PDF files opened with LaTeX Workshop's PDF viewer by default through
  `workbench.editorAssociations`; remove that association to prefer another
  PDF editor.

Run **Format Document** from the Command Palette, or use **Option+Shift+F** with
VS Code's default macOS keybindings. **Format Selection** is also supported.
If prompted, use **Format Document With...** and select **LaTeX Workshop**.
If an old executable path is cached, run **Developer: Reload Window**.

## Global build output and project overrides

Formatting and build output now have user-level defaults, so a project does
not need `.vscode/settings.json` merely to activate them. Project-specific
`latexindent.yaml` is loaded from the detected root TeX file's directory after
the shared style; see [`latexindent.md`](latexindent.md).

Explicit `.vscode` overrides still obey VS Code's folder scope: open the
project as a folder, or add it to a multi-root workspace. Opening only a parent
folder does not activate a child's `.vscode/settings.json`.

The tracked user settings already contain these build defaults; a workspace
may override them when needed:

```json
{
    "latex-workshop.latex.outDir": "%DIR%/build",
    "latex-workshop.latex.auxDir": "%OUTDIR%"
}
```

`%DIR%` is the root TeX file's directory, not necessarily the workspace folder.
The standard `latexmk` tool passes `-outdir=%OUTDIR%` and `-auxdir=%AUXDIR%`;
custom recipes must honor these placeholders too. Build-directory settings have
no trailing slash; the formatter's `-c` directory argument above does.

A project's `.latexmkrc` configures `latexmk`, but explicit command-line
arguments from the extension override it. Setting the extension's output
directory also tells its PDF viewer and SyncTeX integration where to find
outputs. Existing root artifacts are not automatically moved or removed.
See [`latex.md`](latex.md) for the CLI configuration.

## Verify and remove

Open **Preferences: Open User Settings (JSON)** and confirm the shared values
and any required host-specific executable override. Format a temporary copy of
a `.tex` file before enabling format-on-save; check prose, math delimiters,
lists, comments, and verbatim content. For build output, run the standard
`latexmk` recipe and confirm that PDF/auxiliary files appear in `build/`.

To undo deployment, restore the backed-up user settings rather than delete
unrelated customizations. The settings do not install or remove VS Code,
extensions, the TeX distribution, or the formatter. Remove project-specific
settings separately only when intended.
