# latexindent

`latexindent` formats LaTeX source independently of compilation. It is optional
on all profiles; the VS Code integration is for GUI editor clients, not an
instruction to install VS Code on a cluster or headless server. See
[`device-profiles.md`](device-profiles.md) and [`vscode.md`](vscode.md).

## macOS installation and Perl dependencies

A TeX distribution may already provide `latexindent`. Check whether it works,
not merely whether its executable exists:

```sh
command -v latexindent
latexindent --version
```

MacTeX's Perl script can fail with `Can't locate File/HomeDir.pm in @INC`
or another missing Perl module. A Homebrew installation supplies the formatter
and its packaged Perl dependencies without changing macOS's system Perl:

```sh
brew install latexindent
"$(brew --prefix)/bin/latexindent" --version
```

Do not use sudo to add modules to system Perl or replace the system Perl.
Homebrew may install its own Perl dependency; leave unrelated dependencies and
existing TeX distributions intact.

If `/Library/TeX/texbin` precedes Homebrew in PATH, the bare command
`latexindent` may still select MacTeX's broken script after installation.
Rather than changing shell PATH globally, set an absolute executable path in
the installed VS Code user settings. For native Apple Silicon Homebrew:

```json
"latex-workshop.formatting.latexindent.path": "/opt/homebrew/bin/latexindent"
```

An Intel Mac commonly uses `/usr/local/bin/latexindent`; determine the actual
prefix with `brew --prefix`. The tracked `VSCode/settings.json` deliberately
uses the portable name `latexindent`; preserve a working host-specific override
when deploying or refreshing it. Record installed versions, local paths, and
backup locations in that host's `~/admin-docs/`, not here.

## Linux and shared hosts

Use the distribution's formatter/TeX Live packages, including their Perl
runtime dependencies, or an existing working TeX Live executable. Package
names vary by distribution and release. Verify `latexindent --version` before
configuring an editor; a compiler working does not establish that this Perl
formatter works. An existing Homebrew installation can also provide it with
`brew install latexindent`.

On clusters, follow site policy and prefer existing or user-local tools. Do
not install system packages, alter system Perl, or deploy GUI settings there
without the required role and authorization.

## Install the shared style

The user-requested default style is tracked in
[`../.config/latexindent/latexindent.yaml`](../.config/latexindent/latexindent.yaml).
It uses two-space indentation, joins prose paragraphs, keeps list markers with
their opening text, and writes simple displays as `$$ ... $$` on one source line.
Displays containing explicit TeX row breaks (`\\`) retain internal source line
breaks instead of being flattened. The delimiter-edge whitespace is normalized,
keeping the first/last mathematics beside the opening/closing `$$`.
Before indentation/reflow, protected replacement rules convert paired
`\(...\)` to `$...$` and `\[...\]` to `$$...$$`. The display-spacing rule
then normalizes safe converted displays as well. Literal examples in comments
or verbatim content and TeX row breaks such as `\\[2pt]` are not converted.
Reflow stops at trailing comments; comment-bearing math can remain multiline
rather than moving a comment across its terminating newline.
It preserves blank paragraph boundaries, comments, verbatim content, and
explicit TeX row breaks. This is an intentional source-reflow default, not just
visual wrapping. Format-on-save remains off.

Back up existing configuration before deployment; merge existing path lists
rather than overwrite them. Install the style file:

```sh
mkdir -p "$HOME/.config/latexindent"
cp -p ~/dotfiles/.config/latexindent/latexindent.yaml \
  "$HOME/.config/latexindent/latexindent.yaml"
```

A native latexindent user configuration supplies this style even when a project
has no local YAML. For first-time setup, create `~/.indentconfig.yaml` with an
absolute path generated for the current user:

```sh
python3 - <<'PY'
from pathlib import Path
import json
home = Path.home()
config = home / '.indentconfig.yaml'
if config.exists():
    raise SystemExit('Existing user configuration: merge its paths instead.')
style = home / '.config/latexindent/latexindent.yaml'
if not style.is_file():
    raise SystemExit('Install the shared style first.')
config.write_text('paths:\n  - ' + json.dumps(str(style)) + '\n')
PY
```

Do not put a literal `~` or `${HOME}` in the YAML path and assume a shell will
expand it. `LATEXINDENT_CONFIG` and platform-native configurations can take
precedence over `~/.indentconfig.yaml`: for example,
`~/Library/Preferences/latexindent/indentconfig.yaml` on macOS, and
`$XDG_CONFIG_HOME/latexindent/indentconfig.yaml` or
`~/.config/latexindent/indentconfig.yaml` on Linux. If one already exists,
merge the style path there; consult `indent.log` to verify which file is read.

## Global VS Code arguments and project overrides

[`../VSCode/settings.json`](../VSCode/settings.json) selects LaTeX Workshop and
`latexindent` for the `latex` and `tex` modes, keeps visual word wrapping,
uses two-space indentation, and leaves format-on-save off. Its global arguments
are:

```json
"latex-workshop.formatting.latexindent.args": [
    "-m",
    "-rv",
    "-l=%DIR%/latexindent.yaml",
    "-c",
    "%DIR%/build/",
    "%TMPFILE%"
]
```

The native user configuration loads the shared style first. The `-l` argument
then overlays a root-level project `latexindent.yaml`, if present. If absent,
latexindent logs a nonfatal missing-file warning and continues with the shared
style; it does not fail or lose the paragraph/display rules. This fallback was
verified with latexindent 4.0.3. Keep project notation and any exceptions in the
project, not in the shared profile. A global default does not require opening
each project as its own VS Code folder; explicit `.vscode` overrides still do.

LaTeX Workshop formats a temporary input, reads formatted stdout, and applies
an editor edit. `-c` puts persistent logs/backups in the root TeX file's
`build/` directory; it requires the trailing slash. The extension may briefly
create and remove `__latexindent_temp_*.tex` beside the edited document.

Important switches:

- `-l=FILE`: load YAML settings after native user settings. Project-local
  rules can override the shared style without changing the global arguments.
- `-m`: enable the YAML's `modifyLineBreaks` rules; it does not mean overwrite.
- `-rv`: enable replacement rules with comments/verbatim material protected.
  Shared pre-indentation rules normalize paired math delimiters; the final
  display rule checks protected comment/token patterns before joining lines.
  The protection relies on latexindent internals; retest it when upgrading.
- `-w` / `-wd`: overwrite the source (always / only if different), with a backup.
  Do not add these to VS Code arguments; the editor handles applying edits.
- `-d`: ignore native user and local YAML settings. Useful when a CLI caller
  explicitly wants only latexindent's built-in defaults.

Global `-m` and `-rv` mean that a project's own transformation/replacement rules
are enabled too. Only format trusted project YAML, especially Perl replacement
rules. A project can opt out of reflow or use a different formatter through an
explicit workspace setting. No files are mass-formatted merely by setup.

## Verification and removal

Run the selected executable's `--version`. Format copies in projects both with
and without local YAML. Check prose, lists, paragraph boundaries, math,
comments, verbatim material, and explicit TeX row breaks; a second pass should
be stable. Confirm in `indent.log` that the shared style was read. Then use
**Format Document** in VS Code; see [`vscode.md`](vscode.md).

To undo deployment, restore the relevant editor settings and native user
configuration backups. Remove only the shared style path from an existing
native configuration, or remove the newly created `~/.indentconfig.yaml` if it
was created solely for this setup. Remove the installed style separately when
wanted; preserve other configuration paths, project YAML, research sources,
editor sessions, and TeX distributions. Uninstall the Homebrew formatter only
if explicitly wanted with `brew uninstall latexindent`; do not broadly remove
Perl dependencies or run autoremove.
