# Factorio Raw Data
Yet another dump of `data.raw` from Factorio. This one however uses the keys to organize the prototypes into files. `data.raw[type][name]` translates to the file `data/type/name`.

If you're looking for a specific prototype on GitHub, press `t` to search by file name.


# Generation
This isn't on the mod portal, but if for some reason you want to generate this with mod data then setup for this is the following:

1. Download [Factorio headless](https://factorio.com/get-download/latest/headless/linux64) to the `factorio/` directory.
   1a. Optional: Added any desired mods to the `factorio/mod` directory
2. Run the `scripts/build_docs.py` script with python 3.5 or newer (developed on 3.6.8)
3. All prototypes should be in the `data_raw` directory