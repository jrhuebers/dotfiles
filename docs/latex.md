# LaTeX

A usable LaTeX toolchain is required on **every supported machine** (cluster,
personal Linux GUI, personal macOS, and personal headless server). Install a
platform-appropriate TeX distribution that provides a PDF compiler such as
`pdflatex` and the packages needed by the projects on that machine. On Macs,
MacTeX is the standard macOS distribution; on Linux, use TeX Live. A GUI editor
is not required.

## macOS

Install the full TeX Live distribution without GUI applications using MacTeX:

```sh
brew install --cask mactex-no-gui
```

This is a large download and the package installer requires administrator
authorization. If Homebrew reports that a terminal is required for the
password, open the downloaded `mactex-*.pkg` in Finder and complete the
installer there. After installation, make the TeX binaries available in the
current shell:

```sh
eval "$(/usr/libexec/path_helper)"
command -v pdflatex
pdflatex --version
```

A new terminal session also refreshes the PATH. `mactex-no-gui` provides the
same TeX Live toolchain as MacTeX but omits GUI applications such as TeXShop.

## Linux workstation or personal server

Install TeX Live and a PDF compiler using the platform package manager. For
Debian/Ubuntu:

```sh
sudo apt update
sudo apt install texlive-latex-extra latexmk
```

For Fedora:

```sh
sudo dnf install texlive-scheme-medium latexmk
```

On a host without administrative access, use a user-local TeX Live
installation rather than attempting a system install. Verify that its `bin`
directory is in `PATH`.

## Cluster hosts

TeX Live is required on cluster setups too. Use the site's existing TeX Live
when available; otherwise follow the user-local TeX Live installation
procedure documented in the local `~/admin-docs/` for that cluster. Do not use
`sudo` or install system-wide packages on shared cluster hosts. `latexpand` is
an additional cluster requirement for the paper-fetching workflow; see
[`latexpand.md`](latexpand.md).

## Verify

```sh
command -v pdflatex
pdflatex --version
```

Compile a project's `.tex` entry point with `latexmk -pdf <file>.tex` when
`latexmk` is installed, or use `pdflatex <file>.tex` (often twice to resolve
references). Some projects require extra TeX packages or a specific compiler;
follow the project's instructions in those cases.

## Build directories and latexmk configuration

For projects using an isolated output directory, a project-level `.latexmkrc`
(Perl syntax) can contain:

```perl
$out_dir = 'build';
$pdf_mode = 1;
```

Then, from the project directory, `latexmk main.tex` produces a PDF using
pdfLaTeX and writes generated files into `build/`. The equivalent explicit
invocation is:

```sh
latexmk -pdf -outdir=build main.tex
```

`latexmk` reruns the compiler and bibliography/index tools as needed. Explicit
command-line options override the corresponding `.latexmkrc` defaults. Thus an
editor recipe passing a different `-outdir` can override this file.

LaTeX Workshop also needs `latex-workshop.latex.outDir: "%DIR%/build"` and
`latex-workshop.latex.auxDir: "%OUTDIR%"` in the active project/workspace
settings, with a recipe that uses those output directories. See
[`vscode.md`](vscode.md) for the JSON, folder scope, PDF viewer, and SyncTeX
behavior. Existing generated artifacts in the source root are not removed by
changing the output directory.

## Optional source formatting

The compiler/build setup is independent of source formatting. Use
[`latexindent.md`](latexindent.md) for the optional `latexindent` formatter,
Perl dependency troubleshooting, and conservative VS Code defaults. Keep
research-specific notation, macros, and paragraph/display formatting rules in
the research project rather than in this machine-configuration repository.
