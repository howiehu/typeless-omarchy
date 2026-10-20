-- Exercise the actual installed-rule callbacks with live-object/timer fixtures.
local callbacks, timers, focused, dispatched
local function window(class, title, workspace)
  return { class = class, title = title, address = tostring({}), mapped = true,
    hidden = false, visible = true, workspace = { id = workspace or 1 } }
end
local function setup(initial)
  callbacks, timers, focused, dispatched = {}, {}, initial, {}
  o = { window = function() end }
  hl = {
    get_active_window = function() return focused end,
    on = function(event, callback) callbacks[event] = callback end,
    timer = function(callback, opts)
      assert(opts.timeout > 0 and opts.type == "oneshot")
      table.insert(timers, callback)
    end,
    dsp = { focus = function(args) return args end },
    dispatch = function(args) table.insert(dispatched, args.window) end,
  }
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

test("Status restores the preceding visible window", function()
  local target, status = window("probe", "input"), window("Typeless", "Status")
  setup(target); activate(status); flush()
  assert(#dispatched == 1 and dispatched[1] == "address:" .. target.address)
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
print("Passed " .. cases .. " Status focus safety cases")
