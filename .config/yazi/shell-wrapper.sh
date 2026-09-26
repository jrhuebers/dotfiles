#!/usr/bin/env bash

y() {
	local tmp cwd
	tmp="$(mktemp -t yazi-cwd.XXXXXX)" || return
	command yazi "$@" --cwd-file="$tmp"

	if IFS= read -r -d '' cwd < "$tmp" &&
		[[ -n "$cwd" && "$cwd" != "$PWD" && -d "$cwd" ]]; then
		builtin cd -- "$cwd"
	fi

	command rm -f -- "$tmp"
}
