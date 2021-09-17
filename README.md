# Factorio Raw Data
Yet another dump of `data.raw` from Factorio. This one however uses the keys to organize the prototypes into files.
`data.raw[category][name]` translates to the file `data_raw/category/name`.

If you're looking for a specific prototype on GitHub, press `t` to search by file name or use `filename:___` in the
search box.


# Local Setup
This tool assumes a Linux environment with Python 3.5+ (developed on 3.6.8) and Git installed.

[comment]: <> (1. Download [Factorio headless]&#40;https://factorio.com/get-download/latest/headless/linux64&#41; to the `factorio/` directory.)
1. Download [Factorio for Linux](https://www.factorio.com/download) to the `factorio/` directory (bin/data/etc should be
   directly in the factorio directory)
2. Optional: Added any desired mods to the `factorio/mod` directory

Note: This could in theory work with Max or Windows versions of Factorio, but I'm not sure how well the output parsing
will work with them.

NOTE 2: This doesn't currently work with headless, due to instrument mode not working with it. This will hopefully be
fixed soon and will be the supported version moving forward.


# Data Diff
Run `scripts/build_docs.py diff` to build a diff of every mod/data sub-stage in the game. This is done by dumping the
`data.raw` table after every mod runs in every data stage. Running with a bunch of mods may take some time to run.

The diff will be stored in a local branch timestamped for this run, something like `diff-YYYY-MM-DDThh-mm-ss`. Git can
then be used to check the full diff of various files.


# Generation
Run `scripts/build_docs.py final` to dumps the final result of `data.raw` from after all mods run.


# Future Development
* Fix base data.raw dump for repo searching
* Parse while the game is still running
* Refactor to use a docker image for customization and portability
