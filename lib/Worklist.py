import functools
import sys

from pybril.PyBril import PyBril
from util import split_in_blocks
from util import add_terminators
from lib import CFG
import copy


def union(dicts):
    """
    Creates a union of the input dictionaries
    :param dicts: The input dictionaries
    :return: The union
    """
    result = dict()
    for d in dicts:
        for key in d:
            result[key] = d[key]

    return result

def uses(block):
    uses = set()
    wrote_to = set()
    for instr in block.get_instr_list():
        # Reads
        if 'args' in instr:
            for arg in instr['args']:
                if arg not in wrote_to:
                    uses.add(arg)

        if 'dest' in instr:
            wrote_to.add(instr['dest'])

    return uses

def cprop_union(dicts):
    result = dict()

    for d in dicts:
        for key in d:
            if key not in result:
                result[key] = d[key]
            else:
                if d[key] != result[key]:
                    result[key] = "?"

    return result

def cprop_transfer(block, merged):
    result = dict()

    for k in block:
        result[k] = block[k]

    for key in merged:
        if key not in result:
            result[key] = merged[key]
        else:
            if merged[key] != result[key]:
                result[key] = "?"

    return result


def transfer_live(block, inputs):
    """
    Transfer method for the live variables
    :param block: The input block
    :param inputs: The inputs to the block
    :return: The output
    """
    used_vars = uses(block.get_block())
    used_vars = dict(zip(used_vars, range(0, len(used_vars))))

    block_defs = block.get_annotated_definitions()

    sub = [d for d in inputs.items() if d[0] not in block_defs]
    sub = dict(sub)

    sub.update(used_vars)

    return sub

def transfer_reaching(block, inputs):
    """
    Transfer method for reaching definitions
    :param block: The input block
    :param inputs: The inputs to the block
    :return: The output
    """
    block_defs = block.get_annotated_definitions()

    sub = [d for d in inputs.items()]
    sub = dict(sub)

    # By updating, we also overwrite input definitions (if any) with the
    # ones of the current block if they write to the same variable (killed definitions).
    sub.update(block_defs)

    return sub


methods = {
    "reaching": {
        "merge": union,
        "transfer": lambda block, y: transfer_reaching(block, y),
        "inverse": False
    },
    "defined": {
        "merge": union,
        "transfer": lambda block, y: dict(block.get_annotated_definitions(), **y),
        "inverse": False
    },
    "live": {
        "merge": union,
        "transfer": lambda block, y: transfer_live(block, y),
        "inverse": True
    },
    "cprop": {
        "merge": cprop_union,
        "transfer": lambda block, y: cprop_transfer(block.get_block().get_full_definitions(), y),
        "inverse": False
    }
}

def worklist(blocks, method, inverse=False):
    """
    The worklist solver
    :param blocks: The block list
    :param merge_func: The merge function
    :param transfer_func: The transfer function
    :return: A dictionary with the inputs and outputs per block
    """
    merge = methods[method]["merge"]
    transfer = methods[method]["transfer"]

    cfg = CFG(blocks)

    if inverse:
        cfg.switch_directions()

    input  = dict([(node.get_name(), dict()) for node in cfg.nodes.values()])
    output = dict([(node.get_name(), dict()) for node in cfg.nodes.values()])

    nodes = list(cfg.nodes.values())

    while nodes:
        current = nodes.pop(0)

        # Merge the inputs from all incoming edges
        input_values = [output[p] for p in current.get_predecessors()]
        input_values = input_values if input_values else [{}]

        merged = merge(input_values)

        input[current.get_name()].update(merged)

        new_output = transfer(current, merged)

        changed = new_output != output[current.get_name()]
        if changed:
            output[current.get_name()] = new_output
            nodes.append(current)

    return (output, input) if inverse else (input, output)