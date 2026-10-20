-- The recording HUD maps as Status; interactive answers map as AI result.
-- Keep the vendor's interactive controls clickable without focusing on show/hover.
o.window({ class = "^Typeless$", title = "^Status$" }, {
  tag = "-default-opacity",
  float = true,
  pin = true,
  border_size = 0,
  no_shadow = true,
  no_blur = true,
  opacity = "1 1",
  no_focus = false,
  no_follow_mouse = true,
  no_initial_focus = true,
})

-- Answers remain interactive, and follow the user across workspaces.
o.window({ class = "^Typeless$", title = "^AI result$" }, {
  tag = "-default-opacity",
  float = true,
  pin = true,
  border_size = 0,
  no_shadow = true,
  no_blur = true,
  opacity = "1 1",
})

-- Status needs pointer focus for its cancel/confirm controls, but accepting
-- keyboard focus would remove the Fcitx context that receives the result.
-- Restore only the preceding live window on the same workspace. Never write
-- into an unfocused input context or redirect an interactive answer card.
local function is_status(window)
  return window and window.class == "Typeless" and window.title == "Status"
end

local previous = hl.get_active_window()
if is_status(previous) then previous = nil end

hl.on("window.active", function(window)
  if not window or not window.mapped then
    previous = nil
    return
  end
  if not is_status(window) then
    previous = window
    return
  end
  local target = previous
  if not target or not target.mapped or target.hidden then return end
  hl.timer(function()
    if hl.get_active_window() ~= window then return end
    if not target.mapped or target.hidden or not target.visible then return end
    if not target.workspace or not window.workspace or target.workspace.id ~= window.workspace.id then return end
    hl.dispatch(hl.dsp.focus({ window = "address:" .. target.address }))
  end, { timeout = 1, type = "oneshot" })
end)
