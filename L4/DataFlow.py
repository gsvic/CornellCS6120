from pybril.PyBril import PyBril
from util import split_in_blocks
from util import add_terminators
from lib import CFG

import sys


def quick_start():
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"

    some_bril = "./test/branch.bril"
    #some_bril = sys.argv[1]

    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)

    code = brilpy.bril2json(some_bril)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)
        cfg = CFG(blocks)

        for node in cfg.nodes:
            print(str(node) + ":")
            print("  In:  " + str(cfg.nodes[node].get_inputs()))
            print("  Out: " + str(cfg.nodes[node].get_outputs(set())))

        print()


if __name__ == "__main__":
    quick_start()