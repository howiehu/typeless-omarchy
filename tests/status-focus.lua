-- Exercise the actual installed-rule callbacks with live-object/timer fixtures.
local callbacks, timers, focused, dispatched, no_warps, fail_focus, rules, properties, polls
local function window(class, title, workspace)
  return { class = class, title = title, address = tostring({}), mapped = true,
    hidden = false, visible = true, workspace = { id = workspace or 1 } }
end
local function setup(initial)
  callbacks, timers, focused, dispatched = {}, {}, initial, {}
  no_warps, fail_focus = false, false
  rules, properties, polls = {}, {}, {}
  o = { window = function(match, props) table.insert(rules, {match=match, props=props}) end }
  hl = {
    get_active_window = function() return focused end,
    get_windows = function() return {} end,
    get_cursor_pos = function() return hl.cursor end,
    get_config = function(key) assert(key == "cursor:no_warps"); return no_warps end,
    config = function(value) no_warps = value.cursor.no_warps end,
    on = function(event, callback) callbacks[event] = callback end,
    timer = function(callback, opts)
      assert(opts.timeout > 0)
      if opts.type == "repeat" then
        table.insert(polls, callback)
        return {set_enabled = function(_, value) hl.polling = value end}
      end
      assert(opts.type == "oneshot"); table.insert(timers, callback)
    end,
    dsp = { focus = function(args) return args end, window = {set_prop=function(args) return args end}, cursor={move=function(args) return args end} },
    dispatch = function(args)
      if args.prop then table.insert(properties,args); return end
      if args.x then hl.cursor={x=args.x,y=args.y}; return end
      if fail_focus then error("expired dispatcher target") end
      if not no_warps then hl.cursor={x=1200,y=688} end
      table.insert(dispatched, args.window)
    end,
  }
  hl.cursor = {x=17,y=29}
  dofile(arg[1])
end
local function activate(w)
  focused = w
  callbacks["window.active"](w)
end
local function flush()
  for _, callback in ipairs(timers) do callback() end
  timers = {}
end
local cases = 0
local function test(name, fn)
  fn()
  cases = cases + 1
  print("PASS " .. name)
end

test("idle HUD is excluded from pointer focus, active HUD allows controls", function()
  setup(window("probe", "input"))
  local idle = false
  for _, rule in ipairs(rules) do
    if rule.match.title == "^Status [(]idle[)]$" then
      assert(rule.props.no_focus == true); idle = true
    end
  end
  assert(idle and rules[1].props.no_focus == false)
end)
test("transparent parts of a visible HUD pass clicks; only control rectangles accept them", function()
  setup(window("probe", "input"))
  local hud=window("Typeless", "Status [100,200,150,80]")
  hud.at, hud.size = {x=825,y=438}, {x=750,y=500}
  hl.cursor={x=900,y=600}; callbacks["window.title"](hud)
  assert(properties[#properties].value == "true" and #polls==1)
  hl.cursor={x=950,y=670}; polls[1]()
  assert(properties[#properties].value == "false")
  hl.cursor={x=1200,y=800}; polls[1]()
  assert(properties[#properties].value == "true")
  hud.title="Status (idle)"; callbacks["window.title"](hud)
  assert(properties[#properties].value == "true" and hl.polling==false)
end)
test("Status restores the preceding visible window", function()
  local target, status = window("probe", "input"), window("Typeless", "Status")
  setup(target); activate(status); flush()
  assert(#dispatched == 1 and dispatched[1] == "address:" .. target.address)
  assert(hl.cursor.x==17 and hl.cursor.y==29, "cursor moved after restoring focus")
end)
test("desktop-state focus churn restores the cursor captured at activation", function()
  setup(window("probe", "input")); activate(window("Typeless", "Status"))
  hl.cursor={x=1200,y=688}; flush()
  assert(hl.cursor.x==17 and hl.cursor.y==29)
end)
test("ordinary app focus is not redirected", function()
  setup(window("probe", "input")); activate(window("browser", "page")); flush()
  assert(#dispatched == 0)
end)
test("AI result remains interactive", function()
  setup(window("probe", "input")); activate(window("Typeless", "AI result")); flush()
  assert(#dispatched == 0)
end)
test("no stale target when startup focus is Status", function()
  setup(window("Typeless", "Status")); activate(window("Typeless", "Status")); flush()
  assert(#dispatched == 0)
end)
test("focus cleared before Status does not restore an old app", function()
  setup(window("probe", "input")); activate(nil); activate(window("Typeless", "Status")); flush()
  assert(#dispatched == 0)
end)
test("expired window object is treated as cleared focus", function()
  setup(window("probe", "input")); activate({}); activate(window("Typeless", "Status")); flush()
  assert(#dispatched == 0)
end)
for _, property in ipairs({"mapped", "visible"}) do
  test("target becoming " .. property .. "=false is not restored", function()
    local target = window("probe", "input")
    setup(target); activate(window("Typeless", "Status")); target[property] = false; flush()
    assert(#dispatched == 0)
  end)
end
test("hidden target is not restored", function()
  local target = window("probe", "input")
  setup(target); activate(window("Typeless", "Status")); target.hidden = true; flush()
  assert(#dispatched == 0)
end)
test("target on another workspace is not restored", function()
  local target = window("probe", "input")
  setup(target); activate(window("Typeless", "Status", 2)); flush()
  assert(#dispatched == 0)
end)
test("user focus change before timer is respected", function()
  setup(window("probe", "input")); activate(window("Typeless", "Status"))
  activate(window("browser", "page")); flush()
  assert(#dispatched == 0)
end)
test("user cursor policy is restored after focus", function()
  setup(window("probe", "input")); activate(window("Typeless", "Status")); flush()
  assert(no_warps == false)
  setup(window("probe", "input")); no_warps = true
  activate(window("Typeless", "Status")); flush(); assert(no_warps == true)
end)
test("cursor policy is restored even if focus dispatch fails", function()
  setup(window("probe", "input")); fail_focus = true
  activate(window("Typeless", "Status")); pcall(flush); assert(no_warps == false)
end)
print("Passed " .. cases .. " Status focus safety cases")
