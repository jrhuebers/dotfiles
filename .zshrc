precmd() { print "" }
PROMPT=$'%F{green}%n%f@%F{blue}%m%f %F{yellow}%~%f %# '
alias ls='ls -G'
alias dortmund='ssh dortmund -t tmux attach'


. "$HOME/.local/bin/env"

# Added by Antigravity
export PATH="/Users/jhuebers/.antigravity/antigravity/bin:$PATH"
