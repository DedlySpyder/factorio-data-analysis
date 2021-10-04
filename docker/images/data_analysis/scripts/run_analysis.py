#!/usr/bin/env python3

import argparse
import os
import shutil

from factorio_runner import run_factorio
import data_parser

DUMMY_SAVE_NAME = '/tmp/dummy_save'
DUMMY_SAVE_FILE_NAME = DUMMY_SAVE_NAME + '.zip'
OUTPUT_DIR = '/output'


def cleanup_output():
    if os.path.isdir(OUTPUT_DIR):
        print(f'Deleting data directory {OUTPUT_DIR} recursively')
        for fd in os.listdir(OUTPUT_DIR):
            shutil.rmtree(os.path.join(OUTPUT_DIR, fd))


def select_instrument_mod(mode):
    if mode == 'final':
        return 'Factorio_Raw_Data'
    elif mode == 'diff':
        return 'Factorio_Incremental_Raw_Data'
    else:
        raise NotImplementedError(f'Script mode {mode} invalid')


def get_parser(mode, debug=False, trace=False):
    if mode == 'final':
        return data_parser.FinalDataParser(OUTPUT_DIR, debug=debug, trace=trace)
    elif mode == 'diff':
        return data_parser.DiffDataParser(OUTPUT_DIR, debug=debug, trace=trace)
    else:
        raise NotImplementedError(f'No parser found for {mode}')


def main(mode, debug=False, trace=False):
    mod = select_instrument_mod(mode)
    _, lines = run_factorio(
        '--instrument-mod', mod,
        '--create', DUMMY_SAVE_NAME,
        verbose=debug
    )

    cleanup_output()

    parser = get_parser(mode, debug, trace)
    parser.parse_lines(lines)

    if os.path.isfile(DUMMY_SAVE_FILE_NAME):
        os.remove(DUMMY_SAVE_FILE_NAME)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description="""
Runs Factorio and dumps the data.raw from the data stage for analysis. This can either be a final or differential dump
of the data.

The final data dump is the final state of data.raw after all mods have run their data sub-stages.

The differential data dump is the data.raw state after every mod has run a data sub-stage (data, data-updates,
data-final-fixes). The differencing tool is currently a git repository built on top of this data, with a commit for each
data sub-stage.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    arg_parser.add_argument(
        'mode',
        action='store',
        choices=['final', 'diff'],
        help="""select final/differential generation mode"""
    )
    arg_parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='set verbosity level (add up to 2 times for finer logging)'
    )

    args = arg_parser.parse_args()
    main(
        args.mode,
        debug=args.verbose > 0,
        trace=args.verbose > 1
    )
