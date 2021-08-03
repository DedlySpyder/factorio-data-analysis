local dump = require("__Factorio_Raw_Data__/dump")

debug.sethook(function()
    local info = debug.getinfo(2, "nS")
    if info.what == "main" then
        local parts = util.split(info.short_src, "/")

        local modNameRaw = parts[1]
        local modName = string.sub(modNameRaw, 3, #modNameRaw - 2)

        local stageRaw = parts[#parts]
        local stage = string.sub(stageRaw, 1, #stageRaw - 4)
        log("<<START>><<" .. modName .. ">><<" .. stage .. ">>")
        dump()
        log("<<DONE>>")
    end
end, "r")

