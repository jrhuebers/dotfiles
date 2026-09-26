#!/usr/bin/env bash

y() {
	local tmp selection cwd
	tmp="$(mktemp -t yazi-cwd.XXXXXX)" || return
	selection="$(mktemp -t yazi-selection.XXXXXX)" || { command rm -f -- "$tmp"; return 1; }
	YAZI_CD_QUIT_SELECTION="$selection" command yazi "$@" --cwd-file="$tmp"

	IFS= read -r -d '' cwd < "$selection" || :
	if [[ -z "$cwd" ]]; then
		IFS= read -r -d '' cwd < "$tmp" || :
	fi
	if [[ -n "$cwd" && "$cwd" != "$PWD" && -d "$cwd" ]]; then
		builtin cd -- "$cwd"
	fi

	command rm -f -- "$tmp" "$selection"
}
