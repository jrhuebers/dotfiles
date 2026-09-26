#!/usr/bin/env bash

y() {
	local tmp cwd tty_state
	tmp="$(mktemp -t yazi-cwd.XXXXXX)" || return
	tty_state="$(stty -g 2>/dev/null)" || tty_state=""
	command yazi "$@" --cwd-file="$tmp"
	# A blocked opener or abrupt Yazi exit can leave the shell's tty noncanonical.
	[[ -z "$tty_state" ]] || stty "$tty_state" 2>/dev/null || :

	IFS= read -r -d '' cwd < "$tmp" || :
	if [[ -n "$cwd" && "$cwd" != "$PWD" && -d "$cwd" ]]; then
		builtin cd -- "$cwd"
	fi

	command rm -f -- "$tmp"
}
