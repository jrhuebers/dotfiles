# Vim

Vim is the terminal editor used here. The repository configuration is stored in
`.vimrc` and installed as `~/.vimrc`.

## Install and configure

On Fedora:

```sh
sudo dnf install vim-enhanced
```

On macOS:

```sh
brew install vim
```

From a checkout at `~/dotfiles`, deploy the configuration:

```sh
install -m 0644 ~/dotfiles/.vimrc ~/.vimrc
```

The configuration enables syntax/filetype support, line numbers, visible
whitespace, four-space indentation (except Makefiles), incremental highlighted
search, mouse support, wrapped-line movement, and a persistent status line.

## Plugins

Vim plugins are managed with [vim-plug](https://github.com/junegunn/vim-plug).
The configuration declares `Julian/lean.vim` for Lean syntax highlighting.
Install vim-plug and then install the declared plugins with:

```sh
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
vim -Nu ~/.vimrc -n -es +'PlugInstall --sync' +qa
```

On a shared cluster where the tracked `.gitconfig` rewrites GitHub HTTPS URLs to
SSH and the cluster has no GitHub SSH authentication, install the declared
plugin over HTTPS instead:

```sh
GIT_CONFIG_GLOBAL=/dev/null git clone https://github.com/Julian/lean.vim.git \
  ~/.vim/plugged/lean.vim
```

Use `:PlugUpdate` inside Vim to update plugins and `:PlugClean` to remove
plugins no longer declared in `.vimrc`.

## Verify and remove

```sh
vim --version | head -3
vim -Nu ~/.vimrc -n -es +'qa'
```

To remove the deployed configuration, delete `~/.vimrc`. The package can be
removed with `sudo dnf remove vim-enhanced` on Fedora or `brew uninstall vim`
on macOS.
