
export HOME=/cephfs/users/huebers
echo "Changed home directory."

#alias uv="$HOME/.local/bin/uv"
export PATH="/cephfs/users/huebers/.local/bin:$PATH"

PS1='\[\e[38;5;214m\]${debian_chroot:+($debian_chroot)}\[\e[0m\]\
\[\e[38;5;39m\]\u\[\e[0m\]\
\[\e[38;5;244m\]@\[\e[0m\]\
\[\e[38;5;81m\]\h\[\e[0m\]\
\[\e[38;5;244m\]:\[\e[0m\]\
\[\e[1;38;5;46m\]\w\[\e[0m\]\
\[\e[38;5;196m\]\$\[\e[0m\] '
export PS1="$PS1"
#export PROMPT_COMMAND='printf "\n"; '"$PROMPT_COMMAND"
export PROMPT_COMMAND='printf "\n"'

export RES=$HOME/FIM/results/odeon/base_model_for_finetuning/checkpoints

alias ls='ls --color=auto'
alias attach='tmux -S $HOME/.tmux/tmp/default attach'

