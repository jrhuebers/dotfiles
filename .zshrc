precmd() { print "" }
PROMPT=$'%F{green}%n%f@%F{blue}%m%f %F{yellow}%~%f %# '
alias ls='ls -G'
alias dortmund='ssh dortmund -t tmux attach'
alias python='python3'
alias pip='pip3'


# User-local tools and the standalone Pi installer.
typeset -U path PATH
path=("$HOME/.local/bin" "$HOME/.pi/agent/bin" $path)
[ ! -r "$HOME/.local/bin/env" ] || . "$HOME/.local/bin/env"

# Optional Antigravity installation on this Mac.
if [ -d "$HOME/.antigravity/antigravity/bin" ]; then
    path=("$HOME/.antigravity/antigravity/bin" $path)
fi

export EDITOR=vim
export VISUAL=vim
[ ! -r "$HOME/.config/yazi/shell-wrapper.sh" ] || . "$HOME/.config/yazi/shell-wrapper.sh"
