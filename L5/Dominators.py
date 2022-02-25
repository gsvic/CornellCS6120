import json
import fileinput
import sys

from pybril.PyBril import PyBril
from util import split_in_blocks
from util import add_terminators
from lib import CFG

import functools


def find_dominators(json_input):
    code = json.loads(json_input)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)

        cfg = CFG(blocks, add_entry_block=True)

        return cfg.get_dominators()

def get_dominators_tree(json_input):
    code = json.loads(json_input)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)

        cfg = CFG(blocks, add_entry_block=True)

        return cfg.get_immediate_dominators()

def get_dominaton_frontiers(json_input):
    code = json.loads(json_input)

    for function in code["functions"]:
        blocks = split_in_blocks(function)
        blocks = add_terminators(blocks)

        cfg = CFG(blocks, add_entry_block=True)

        return cfg.get_domination_frontiers()


if __name__ == "__main__":
    input_json = sys.stdin.read()

    stdout = None
    if len(sys.argv) == 1 or sys.argv[1] == "dom":
        stdout = find_dominators(input_json)
    elif sys.argv[1] == "front":
        stdout = get_dominaton_frontiers(input_json)
    elif sys.argv[1] == "domtree":
        stdout = get_dominaton_frontiers(input_json)

    print(json.dumps(stdout, indent=2))
