local dump = require("__Factorio_Raw_Data__/dump")

local data_stages = {
    data = true,
    ["data-updates"] = true,
    ["data-final-fixes"] = true
}

log("<<START - FactorioDataRawDump>>")
debug.sethook(function()
    local info = debug.getinfo(2, "nS")
    if info.what == "main" then
        local parts = util.split(info.short_src, "/")

        local modNameRaw = parts[1]
        local modName = string.sub(modNameRaw, 3, #modNameRaw - 2)

        local stageRaw = parts[#parts]
        local stage = string.sub(stageRaw, 1, #stageRaw - 4)

        if data_stages[stage] then
            log("<<START>><<" .. modName .. ">><<" .. stage .. ">>")
            dump()
            log("<<DONE>>")
        end
    end
end, "r")
