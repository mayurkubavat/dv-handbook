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
  end
  el.attributes["include"] = nil
  if not el.attributes["filename"] then el.attributes["filename"] = path end
  return el
end
