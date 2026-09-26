local M = { pending_quit = false }

function M:setup()
	ps.sub("cd", function()
		if not self.pending_quit then return end
		self.pending_quit = false
		ya.emit("quit", {})
	end)
end

--- @sync entry
function M:entry()
	local h = cx.active.current.hovered
	if not h then return end

	if h.cha.is_dir then
		self.pending_quit = true
		ya.emit("cd", { h.url })
	else
		ya.emit("open", { hovered = true })
	end
end

return M
