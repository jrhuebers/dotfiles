--- @sync entry
return {
	entry = function()
		local h = cx.active.current.hovered
		if not h then return end

		if h.cha.is_dir then
			ya.emit("cd", { h.url })
			ya.emit("quit", {})
		else
			ya.emit("open", { hovered = true })
		end
	end,
}
