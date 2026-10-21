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

Install and verify `latexindent` using [`latexindent.md`](latexindent.md).
The tracked settings use the portable executable name `latexindent`. On a Mac
where MacTeX's executable shadows Homebrew's working copy, set the installed
user setting `latex-workshop.formatting.latexindent.path` to the absolute
Homebrew path described in that guide. Do not overwrite this host-specific
path when refreshing settings from the repository.

The shared defaults for both `latex` and `tex` language modes are:

- Visual word wrapping on, without inserting source line breaks.
- LaTeX Workshop as the formatter, with two-space indentation.
- Format-on-save explicitly off; Python's separate Ruff settings are unchanged.
- `latexindent` arguments `-c`, `%DIR%/build/`, `%TMPFILE%`, and
  `-y=defaultIndent: '  '`. Persistent formatter logs go into `build/`.
- No global `-m` line-break transformations, replacement rules, or project YAML
  loading. Project-specific prose/display rules belong with their source files.
- PDF files opened with LaTeX Workshop's PDF viewer by default through
  `workbench.editorAssociations`; remove that association to prefer another
  PDF editor.

Run **Format Document** from the Command Palette, or use **Option+Shift+F** with
VS Code's default macOS keybindings. **Format Selection** is also supported.
If prompted, use **Format Document With...** and select **LaTeX Workshop**.
If an old executable path is cached, run **Developer: Reload Window**.

## Project settings and build output

Keep project-specific formatting in `latexindent.yaml` and activate it with
formatter arguments in that project's `.vscode/settings.json`; see
[`latexindent.md`](latexindent.md). A nested `.vscode` directory is not used
merely because a file is inside it: open the project as a VS Code folder, or
add it as a folder in a multi-root workspace. Opening only its parent folder
does not activate the child's settings.

For a project that keeps generated artifacts in `build/`, add:

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
