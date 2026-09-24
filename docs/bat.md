# bat

`bat` is a user-local `cat` alternative with syntax highlighting, line numbers,
Git change markers, themes, and automatic paging. The upstream project is
[`sharkdp/bat`](https://github.com/sharkdp/bat).

## Linux x86_64 cluster installation

Cluster hosts share `~/` through `/nfs_home`, so this installation is visible
on other compatible cluster login/compute hosts. It is installed outside the
system package manager:

- binary: `~/.local/opt/bat-<version>-x86_64-unknown-linux-gnu/bat`
- launcher: `~/.local/bin/bat`
- Bash completion: `~/.local/share/bash-completion/completions/bat`
- Zsh completion: `~/.local/share/zsh/site-functions/_bat`

The current installation uses the official upstream release archive:

```sh
version=0.26.1
archive="bat-v${version}-x86_64-unknown-linux-gnu.tar.gz"
url="https://github.com/sharkdp/bat/releases/download/v${version}/${archive}"
mkdir -p ~/.local/opt ~/.local/bin
curl --fail --location --retry 3 "$url" -o "/tmp/$archive"
tar -xzf "/tmp/$archive" -C ~/.local/opt
mv ~/.local/opt/bat-v${version}-x86_64-unknown-linux-gnu \
  ~/.local/opt/bat-${version}-x86_64-unknown-linux-gnu
ln -sfn ~/.local/opt/bat-${version}-x86_64-unknown-linux-gnu/bat \
  ~/.local/bin/bat
```

On this host, the downloaded archive's SHA-256 was
`726f04c8f576a7fd18b7634f1bbf2f915c43494c1c0f013baa3287edb0d5a2a3`.
Verify the downloaded archive against a trusted upstream checksum when one is
provided for a future release.

Ubuntu/Debian users with administrative access can instead use
`sudo apt install bat`; some older releases expose the command as `batcat`.
Homebrew users can use `brew install bat` on macOS or Linux. Windows users can
use `winget install sharkdp.bat`.

## Usage

```sh
bat README.md
bat -n script.py
bat --style=plain file.txt
bat --paging=never file.txt
bat -A file.txt                    # show non-printable characters
printf 'hello\n' | bat --paging=never
```

`bat` automatically uses plain output when piped or redirected. Use
`--style=plain --paging=never` when a command must produce deliberately clean,
non-interactive output. Keep `/bin/cat` for scripts where the smallest and most
portable raw concatenation tool is preferred.

To preview it without changing the `cat` command:

```sh
alias bcat='bat --paging=never'
```

An optional `cat` alias is:

```sh
alias cat='bat --paging=never'
```

Do not enable that alias in scripts or in a shared profile without checking
compatibility first.

## Verification

```sh
bat --version
bat --list-languages | head
printf 'print("ok")\n' | bat --language=python --paging=never
```

## Removal

```sh
rm -f ~/.local/bin/bat
rm -rf ~/.local/opt/bat-*
rm -f ~/.local/share/bash-completion/completions/bat
rm -f ~/.local/share/zsh/site-functions/_bat
```
