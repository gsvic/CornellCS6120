import json
from lib import LoopPass
from util import split_in_blocks, add_terminators


def licm(code):
    # Init blocks
    for func in code["functions"]:
        blocks = split_in_blocks(func)
        blocks = add_terminators(blocks)

        loop_pass = LoopPass(blocks)
        new_blocks = loop_pass.execute_pass()
        instrs = list()

        for block in new_blocks:
            for inst in block.get_instr_list():
                instrs.append(inst)
        func["instrs"] = instrs

    return code