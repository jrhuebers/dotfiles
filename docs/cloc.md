# cloc

`cloc` counts source-code lines by language. It is a required baseline program:
install it on every machine.

## Install

Use the native package manager on each machine.

Ubuntu/Debian:

```sh
sudo apt update
sudo apt install cloc
```

Fedora/RHEL:

```sh
sudo dnf install cloc
```

macOS with Homebrew:

```sh
brew install cloc
```

On Ubuntu hosts where `sudo` is unavailable, install the Debian package and
its Perl dependencies in the user-local tree:

```sh
packages=(
  cloc libalgorithm-diff-perl libparallel-forkmanager-perl libregexp-common-perl
  libmoo-perl libclass-method-modifiers-perl libclass-xsaccessor-perl
  libimport-into-perl librole-tiny-perl libscalar-list-utils-perl libsub-quote-perl
  libmodule-runtime-perl libparams-classify-perl
)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(
  cd "$tmp"
  apt-get download "${packages[@]}"
)
version=$(dpkg-deb -f "$tmp"/cloc_*.deb Version)
target="$HOME/.local/opt/cloc-$version"
rm -f "$HOME/.local/bin/cloc"
rm -rf "$target"
mkdir -p "$target" "$HOME/.local/bin"
for package in "$tmp"/*.deb; do
  dpkg-deb -x "$package" "$target"
done
cat > "$HOME/.local/bin/cloc" <<EOF
#!/bin/sh
set -eu
root="$target"
perl_libs="\$root/usr/share/perl5:\$root/usr/lib/x86_64-linux-gnu/perl5/5.38:\$root/usr/lib/x86_64-linux-gnu/perl/5.38:\$root/usr/lib/x86_64-linux-gnu/perl-base"
if [ -n "\${PERL5LIB:-}" ]; then
  perl_libs="\$perl_libs:\$PERL5LIB"
fi
export PERL5LIB="\$perl_libs"
exec /usr/bin/perl "\$root/usr/bin/cloc" "\$@"
EOF
chmod 0755 "$HOME/.local/bin/cloc"
```

The user-local method assumes a 64-bit Ubuntu 24.04 Perl layout. Prefer the
native package installation when administrative access is available.

## Verify

```sh
cloc --version
printf 'print("ok\\n")\\n' | cloc --stdin-name smoke.py -
```

The expected version on the current Ubuntu host is `1.98`. Keep
`~/.local/bin` in `PATH`; the tracked Bash profile in this repository does that.

## Remove

For a system installation, use the matching package manager, for example
`sudo apt remove cloc`. For the user-local installation, remove its launcher
and extracted version directory:

```sh
rm -f ~/.local/bin/cloc
rm -rf ~/.local/opt/cloc-<version>
```
