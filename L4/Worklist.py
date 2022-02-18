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


def transfer_live(block, inputs):
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
        current = nodes[0]
        nodes.remove(current)

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


methods = {
    "defined": {
        "merge": union,
        "transfer": lambda block, y: dict(block.get_annotated_definitions(), **y),
        "output": lambda x: [pair[0] for pair in x],
        "inverse": False
    },
    "live": {
        "merge": union,
        "transfer": lambda block, y: transfer_live(block, y),
        "output": lambda x: [pair[0] for pair in x],
        "inverse": True
    },
    "cprop": {
        "merge": union,
        "transfer": lambda x, y: union([x, y]),
        "output": lambda x: ["{}:{}".format(pair[0], pair[1]) for pair in x]
    }
}


if __name__ == "__main__":
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"
    some_bril = "./test/fact.bril"  # sys.argv[1]
    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)
    code = brilpy.bril2json(some_bril)

    # Init blocks
    blocks = split_in_blocks(code["functions"][0])
    blocks = add_terminators(blocks)

    method = "defined"

    input, output = worklist(blocks,
                             merge=methods[method]["merge"],
                             transfer=methods[method]["transfer"],
                             inverse=methods[method]["inverse"])

    for block in blocks:
        in_items = sorted(input[block.get_name()].items())
        out_items = sorted(output[block.get_name()].items())

        print(str(block.get_name()) + ":")
        print("  In:  " + str(methods[method]["output"](in_items)))
        print("  Out: " + str(methods[method]["output"](out_items)))