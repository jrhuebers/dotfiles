case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

PS1='\[\e[38;5;214m\]${debian_chroot:+($debian_chroot)}\[\e[0m\]\
\[\e[38;5;39m\]\u\[\e[0m\]\
@\
\[\e[38;5;81m\]\h\[\e[0m\]\
:\
\[\e[1;38;5;46m\]\w\[\e[0m\]\
$ '
export PS1
export PROMPT_COMMAND='printf "\n"'

alias ls='ls --color=auto'
alias squeue='squeue --format="%.18i %.9P %.30j %.8u %.2t %.10M %.6D %R"'
alias attach='tmux -S "$HOME/.tmux/tmp/default" attach'
