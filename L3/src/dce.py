import json
import fileinput

from util import split_in_blocks


def dce_pass(blocks):
    """
    Eliminates dead code for a sequence of blocks
    :param blocks: The sequence of blocks
    :return: The "cleaned" blocks
    """
    # Mark instructions to be deleted
    for block in blocks:
        delete = [None]

        instructions = dict(zip(range(0, len(block)), block))

        while delete:
            used = {}
            last_seen = {}
            delete = list()
            for pair in instructions.items():
                idx = pair[0]
                instr = pair[1]

                # Mark instructions as used, if found in arguments
                if 'args' in instr:
                    for arg in instr['args']:
                        used[arg] = True

                if 'dest' in instr:
                    var_name = instr['dest']

                    # Mark for deletion an instruction that we have seen again and
                    # it is not used until now
                    if var_name in last_seen and not used[var_name]:
                        delete.append(last_seen[var_name])

                    # Mark an instruction that we see for the first time as not used
                    if var_name not in used:
                        used[var_name] = False

                    # Store the last position we saw this variable
                    last_seen[var_name] = idx

            # Also mark for deletion instructions that are never used
            for instr in used:
                if not used[instr]:
                    delete.append(last_seen[instr])

            for idx in delete:
                instructions.pop(idx)

            block[:] = list(instructions.values())

    return blocks

def trivial_dce_pass(blocks):
    """
    The trivial dead code elimination
    :param blocks: The sequence of blocks
    :return: The "cleaned" blocks
    """
    changed = True

    while changed:
        used = {}
        for block in blocks:
            delete = list()
            for instr in block:
                # Mark instructions as used, if found in arguments
                if 'args' in instr:
                    for arg in instr['args']:
                        used[arg] = True

        for block in blocks:
            prev_len = len(block)
            block[:] = [instr for instr in block if 'dest' not in instr or instr['dest'] in used]

            changed = prev_len != len(block)

    return list(blocks)


if __name__ == "__main__":
    input_json = ""
    for line in fileinput.input():
        input_json += line

    input_json = json.loads(input_json)


    for func in input_json["functions"]:
        blocks = split_in_blocks(func)
        clean = [inst for block in trivial_dce_pass(blocks) for inst in block]
        func['instrs'] = clean


    print(json.dumps(input_json, indent=1))