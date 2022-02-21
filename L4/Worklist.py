import functools
import sys

from pybril.PyBril import PyBril
from util import split_in_blocks
from util import add_terminators
from lib import CFG


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


def worklist(blocks, merge, transfer, inverse=False):
    """
    The worklist solver
    :param blocks: The block list
    :param merge: The merge function
    :param transfer: The transfer function
    :return: A dictionary with the inputs and outputs per block
    """
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


def write_to_stdout(input, output, var_names_only=True):
    """
    Formats and prints the inputs/outputs per block
    :param input: The input list
    :param output: The output list
    :return: None
    """
    for block in blocks:
        if var_names_only:
            in_items = sorted(input[block.get_name()].keys())
            out_items = sorted(output[block.get_name()].keys())
        else:
            in_items = sorted(input[block.get_name()].items())
            in_items = list(map(lambda x: "{}: {}".format(x[0], x[1]), in_items))
            out_items = sorted(output[block.get_name()].items())
            out_items = list(map(lambda x: "{}: {}".format(x[0], x[1]), out_items))

        if not in_items:
            in_items = "∅"
        else:
            in_items = functools.reduce(lambda x, y: "{}, {}".format(x, y), in_items)

        if not out_items:
            out_items = "∅"
        else:
            out_items = functools.reduce(lambda x, y: "{}, {}".format(x, y), out_items)

        print(str(block.get_name()) + ":")
        print("  in:  " + str(in_items))
        print("  out: " + str(out_items))


methods = {
    "defined": {
        "merge": union,
        "transfer": lambda block, y: dict(block.get_annotated_definitions(), **y),
        "output": lambda input, output: write_to_stdout(input, output, var_names_only=True),
        "inverse": False
    },
    "live": {
        "merge": union,
        "transfer": lambda block, y: transfer_live(block, y),
        "output": lambda input, output: write_to_stdout(input, output, var_names_only=True),
        "inverse": True
    },
    "cprop": {
        "merge": cprop_union,
        "transfer": lambda block, y: cprop_transfer(block.get_block().get_full_definitions(), y),
        "output": lambda input, output: write_to_stdout(input, output, var_names_only=False),
        "inverse": False
    }
}


if __name__ == "__main__":
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"
    some_bril = sys.argv[1]
    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)
    code = brilpy.bril2json(some_bril)

    # Init blocks
    blocks = split_in_blocks(code["functions"][0])
    blocks = add_terminators(blocks)

    m = sys.argv[2]
    method = methods[m]

    input, output = worklist(blocks,
                             merge=method["merge"],
                             transfer=method["transfer"],
                             inverse=method["inverse"])

    method["output"](input, output)
