#!/usr/bin/env bash

y() {
	local tmp selection cwd tty_state
	tmp="$(mktemp -t yazi-cwd.XXXXXX)" || return
	selection="$(mktemp -t yazi-selection.XXXXXX)" || { command rm -f -- "$tmp"; return 1; }
	tty_state="$(stty -g 2>/dev/null)" || tty_state=""
	YAZI_CD_QUIT_SELECTION="$selection" command yazi "$@" --cwd-file="$tmp"
	# A blocked opener or abrupt Yazi exit can leave the shell's tty noncanonical.
	[[ -z "$tty_state" ]] || stty "$tty_state" 2>/dev/null || :

	IFS= read -r -d '' cwd < "$selection" || :
	if [[ -z "$cwd" ]]; then
		IFS= read -r -d '' cwd < "$tmp" || :
	fi
	if [[ -n "$cwd" && "$cwd" != "$PWD" && -d "$cwd" ]]; then
		builtin cd -- "$cwd"
	fi

	command rm -f -- "$tmp" "$selection"
}
