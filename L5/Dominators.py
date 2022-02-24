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

def get_dominators_tree(input):
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"

    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)

    code = brilpy.bril2json(input)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)

        cfg = CFG(blocks, add_entry_block=True)

        return cfg.get_immediate_dominators()

print(json.dumps(find_dominators("/Users/victorgiannakouris/Dev/CornellCS6120/L5/test/resources/dominators/loopcond.bril"), indent=4))