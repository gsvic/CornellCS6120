import json
import fileinput

from util import split_in_blocks

COMMUTATIVE_OPS = ["add", "mul", "and", "or", "eq"]

def lvn(blocks):
    """
    Local Value Numbering
    :param blocks: The sequence of blocks
    :return: The rewritten blocks
    """
    for block in blocks:
        instructions = dict(zip(range(0, len(block)), block))

        expr_to_id = {}
        var_to_id = {}
        state = {}

        id = 1

        for pair in instructions.items():
            idx = pair[0]
            instr = pair[1]

            if 'dest' in instr:
                var_name = instr['dest']

                if 'value' in instr:
                    expr = (instr['op'], instr['value'])

                elif 'args' in instr:
                    args = instr['args']
                    op = instr['op']

                    if op in COMMUTATIVE_OPS:
                        args = sorted(args)

                    args = list(map(lambda x: var_to_id[x] if x in var_to_id else x, args))
                    instr['args'] = list(map(lambda x: state[x]['var'] if x in state else x, args))
                    expr = (op, *args)

                # Found an expression already computed
                if str(expr) in expr_to_id:
                    var_to_id[var_name] = expr_to_id[str(expr)]

                else:
                    state[id] = {"expr": expr, "var": instr["dest"]}
                    expr_to_id[str(expr)] = id
                    var_to_id[var_name] = id

                    id += 1
    return blocks


if __name__ == "__main__":
    input_json = ""
    for line in fileinput.input():
        input_json += line

    input_json = json.loads(input_json)


    for func in input_json["functions"]:
        blocks = split_in_blocks(func)
        clean = [inst for block in lvn(blocks) for inst in block]
        func['instrs'] = clean

    print(json.dumps(input_json, indent=1))