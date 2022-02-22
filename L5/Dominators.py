import json

from pybril.PyBril import PyBril
from util import split_in_blocks
from util import add_terminators
from lib import CFG

import functools


def find_dominators(input):
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"

    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)

    code = brilpy.bril2json(input)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)

        cfg = CFG(blocks, add_entry_block=True)

        return cfg.get_dominators()
