import json
from L6 import do_ssa
from util import split_in_blocks, add_terminators

if __name__ == "__main__":
    # BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"
    # some_bril = "/Users/victorgiannakouris/Dev/CornellCS6120/L6/ssa.bril"
    # brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)
    # code = brilpy.bril2json(some_bril)

    code = json.load(open("/Users/victorgiannakouris/Dev/CornellCS6120/L6/test/resources/loop-orig.json"))

    # Init blocks
    blocks = split_in_blocks(code["functions"][0])
    blocks = add_terminators(blocks)

    do_ssa(code)

