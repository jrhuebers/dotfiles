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

## Conservative shared settings

[`../VSCode/settings.json`](../VSCode/settings.json) selects LaTeX Workshop and
`latexindent` for the `latex` and `tex` modes, keeps visual word wrapping,
uses two-space indentation, and leaves format-on-save off. The shared arguments
are:

```json
"latex-workshop.formatting.latexindent.args": [
    "-c",
    "%DIR%/build/",
    "%TMPFILE%",
    "-y=defaultIndent: '  '"
]
```

LaTeX Workshop formats a temporary input, reads formatted stdout, and applies
an editor edit. `-c` puts persistent logs/backups in the root TeX file's
`build/` directory; it requires the trailing slash. The extension may briefly
create and remove `__latexindent_temp_*.tex` beside the edited document.

There is no shared `-m` or replacement flag, so these defaults do not enable
prose reflow, single-line paragraphs, or display rewriting. Visual wrapping is
only an editor display feature; source formatting can change actual line
breaks when explicitly configured.

## Project-specific YAML

Keep `latexindent.yaml` and notation-specific formatting rules in each research
project, not in dotfiles. Merely creating the file does not activate it under
the shared arguments: load it explicitly with `-l` and enable its line-break
rules with `-m`. For example, in the project's `.vscode/settings.json`:

```json
{
    "latex-workshop.formatting.latex": "latexindent",
    "latex-workshop.formatting.latexindent.args": [
        "-m",
        "-l=%DIR%/latexindent.yaml",
        "-c",
        "%DIR%/build/",
        "%TMPFILE%"
    ]
}
```

Open that project as the VS Code folder (or a folder in a multi-root workspace)
for its `.vscode` settings to apply. Opening a parent folder alone does not
activate a nested project's settings. Shared user settings still supply the
formatter path unless the project overrides it.

Important switches:

- `-l=FILE`: load YAML settings, including indentation and optional rules.
- `-m`: enable the YAML's `modifyLineBreaks` rules. It does not itself mean
  overwrite, nor does it require one particular wrapping style.
- `-rv`: enable replacement rules while respecting protected verbatim content;
  use only if the project's YAML needs replacements. A narrow post-indentation
  rule may also inspect protected comment tokens. Keep such implementation-
  specific rules with the project and retest when upgrading the formatter.
- `-w` / `-wd`: overwrite the source (always / only if different), with a backup.
  Do not add these to the VS Code arguments; the editor handles applying edits.

Test paragraph and display normalization on copies, particularly around `%`
comments, inline/verbatim code, `$$` delimiters, and explicit TeX row breaks
(`\\`). Do not silently move comments or change mathematical notation, and do
not mass-format working research sources as a side effect of editor setup.

## Verification and removal

Run the chosen executable's `--version` and format a temporary copy with the
configured arguments. Check that only intended whitespace changes, paragraph
boundaries and math are preserved as appropriate, and a second formatting pass
is stable. Then use **Format Document** in VS Code; see
[`vscode.md`](vscode.md) for shortcuts and setup.

To undo the editor configuration, restore the relevant settings backup or
remove only its LaTeX formatter keys. Uninstall the Homebrew formatter, if
explicitly wanted, with `brew uninstall latexindent`; do not run broad cleanup
or remove Perl dependencies without checking their other users. Preserve TeX
distributions, project YAML files, research sources, and editor sessions.
