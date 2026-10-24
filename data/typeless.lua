-- Omarchy's source scanner substitutes callable proxy tables for runtime APIs.
-- Iterating that proxy with ipairs never terminates. Skip the entire runtime
-- integration before registering rules/events/timers in a scan environment.
if type(hl.get_windows) ~= "function" then return end

-- The recording HUD maps as Status; interactive answers map as AI result.
-- Keep the vendor's interactive controls clickable without focusing on show/hover.
o.window({ class = "^Typeless$", title = "^Status.*$" }, {
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

-- The version-guarded runtime marks an empty canvas with this exact title.
-- Unlike Electron's Wayland input-shape path, compositor hit-testing honors it.
o.window({ class = "^Typeless$", title = "^Status [(]idle[)]$" }, {
  no_focus = true,
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
  return window and window.class == "Typeless" and window.title and window.title:match("^Status")
end

-- Electron's Wayland input region does not exclude the transparent canvas on
-- this build. The guarded runtime places only numeric control rectangles in
-- the HUD title. Use compositor coordinates, not Electron's 0,0 window origin.
local huds, pointer_state = {}, {}
local pointer_timer
local function refresh_hud(window)
  local address = window.address
  if not window.mapped or not address then return false end
  local encoded = window.title:match("^Status %[(.+)%]$")
  local inside = false
  if encoded and window.visible and window.at and window.size then
    local cursor, at, size = hl.get_cursor_pos(), window.at, window.size
    if size.x > 0 and size.y > 0 then
      local x, y = (cursor.x - at.x) * 750 / size.x, (cursor.y - at.y) * 500 / size.y
      for left, top, width, height in encoded:gmatch("(%d+),(%d+),(%d+),(%d+)") do
        local l, t, w, h = tonumber(left), tonumber(top), tonumber(width), tonumber(height)
        if x >= l and x < l + w and y >= t and y < t + h then inside = true; break end
      end
    end
  elseif window.title == "Status" then
    -- Legacy/base-only launches have no region metadata.
    inside = true
  end
  local excluded = not inside
  if pointer_state[address] ~= excluded then
    hl.dispatch(hl.dsp.window.set_prop({ window = "address:" .. address,
      prop = "no_focus", value = excluded and "true" or "false" }))
    pointer_state[address] = excluded
  end
  return encoded ~= nil
end
local function refresh_huds()
  local has_controls = false
  for address, window in pairs(huds) do
    if not window.mapped then huds[address], pointer_state[address] = nil, nil
    else has_controls = refresh_hud(window) or has_controls end
  end
  if pointer_timer then pointer_timer:set_enabled(has_controls) end
  return has_controls
end
local function update_hud(window)
  if not is_status(window) or not window.address then return end
  huds[window.address], pointer_state[window.address] = window, nil
  local has_controls = refresh_huds()
  if has_controls and not pointer_timer then
    pointer_timer = hl.timer(refresh_huds, { timeout = 8, type = "repeat" })
  end
end
hl.on("window.open", update_hud)
hl.on("window.title", update_hud)
for _, window in ipairs(hl.get_windows()) do update_hud(window) end

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
  local cursor = hl.get_cursor_pos()
  hl.timer(function()
    if hl.get_active_window() ~= window then return end
    if not target.mapped or target.hidden or not target.visible then return end
    if not target.workspace or not window.workspace or target.workspace.id ~= window.workspace.id then return end
    -- Restore the cursor in the same synchronous callback if the focus
    -- dispatcher warps it. Changing no_warps around one dispatch is not
    -- sufficient on the tested build; never change the user's global policy.
    local ok, err = pcall(function()
      hl.dispatch(hl.dsp.focus({ window = "address:" .. target.address }))
    end)
    local after = hl.get_cursor_pos()
    if after.x ~= cursor.x or after.y ~= cursor.y then
      hl.dispatch(hl.dsp.cursor.move({ x = cursor.x, y = cursor.y }))
    end
    if not ok then error(err) end
  end, { timeout = 1, type = "oneshot" })
end)
