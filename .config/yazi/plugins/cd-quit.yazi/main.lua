--- @sync entry
return {
	entry = function()
		local h = cx.active.current.hovered
		if not h then return end

		if h.cha.is_dir then
			local selection = os.getenv("YAZI_CD_QUIT_SELECTION")
			if not selection then return ya.emit("enter", {}) end

			local file, err = io.open(selection, "wb")
			if not file then return ya.err("Cannot save selected directory: " .. tostring(err)) end
			local written, write_err = file:write(tostring(h.url))
			local closed, close_err = file:close()
			if not written or not closed then
				return ya.err("Cannot save selected directory: " .. tostring(write_err or close_err))
			end
			ya.emit("quit", {})
		else
			ya.emit("open", { hovered = true })
		end
	end,
}
