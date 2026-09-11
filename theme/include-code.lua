-- theme/include-code.lua -- splice a source file into a fenced code block.
--
--   ```{.makefile include="examples/common.mk"}
--   ```
--
-- The path is relative to the project root, so the printed listing is the
-- exact file that scripts/check-examples.sh compiles and runs.
local function project_root()
  if quarto and quarto.project and quarto.project.directory then
    return quarto.project.directory
  end
  return "."
end

function CodeBlock(el)
  local path = el.attributes["include"]
  if not path then return nil end
  local full = project_root() .. "/" .. path
  local f = io.open(full, "r")
  if not f then
    io.stderr:write("include-code.lua: cannot open " .. full .. "\n")
    el.text = "-- MISSING FILE: " .. path
  else
    el.text = f:read("a"):gsub("\t", "    "):gsub("%s+$", "")
    f:close()
    -- lines="a-b" splices a range, so one output file can follow each of
    -- the designs it reports on instead of arriving as one block after both.
    local range = el.attributes["lines"]
    if range then
      local a, b = range:match("^(%d+)%-(%d+)$")
      local kept, i = {}, 0
      for line in (el.text .. "\n"):gmatch("(.-)\n") do
        i = i + 1
        if i >= tonumber(a) and i <= tonumber(b) then kept[#kept + 1] = line end
      end
      el.text = table.concat(kept, "\n")
      el.attributes["lines"] = nil
    end
  end
  el.attributes["include"] = nil
  if not el.attributes["filename"] then el.attributes["filename"] = path end
  -- A short *output* block is kept whole on one page. A simulator output
  -- whose point is the order of two tools' lines is worthless with the
  -- tools on different pages, and three such blocks were split at a page
  -- foot. Source listings are left to break: asking for space for them
  -- left a third of a page blank ahead of one.
  -- A source listing may break, but not after two lines at a page foot:
  -- it asks for five, which no page can fail to give without a visible
  -- blank, so an orphaned header line cannot happen.
  if FORMAT:match("latex") then
    local _, lines = el.text:gsub("\n", "")
    local need = 5
    if el.classes:includes("text") then need = math.min(lines + 3, 18) end
    return {pandoc.RawBlock("latex",
                            "\\Needspace{" .. need .. "\\baselineskip}"),
            el}
  end
  return el
end
