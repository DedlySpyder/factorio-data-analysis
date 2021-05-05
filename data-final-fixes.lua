for category, prototypes in pairs(data.raw) do
    for name, prototype in pairs(prototypes) do
        log("FactorioDataRawDump(<<" .. category .. ">>,<<" .. name .. ">>,<<" .. serpent.block(prototype, {comment = true, refcomment = true, tablecomment = false}) .. ">>)")
    end
end
log("DONE")
