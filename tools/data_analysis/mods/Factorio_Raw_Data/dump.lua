return function()
    for category, prototypes in pairs(data.raw) do
        for name, prototype in pairs(prototypes) do
            log(string.format(
                    "FactorioDataAnalysisPrototypeStart(<<%s>>,<<%s>>,<<%s>>)FactorioDataAnalysisPrototypeEnd",
                    category,
                    name,
                    serpent.block(prototype, {comment = true, refcomment = true, tablecomment = false})
            ))
        end
    end
end
