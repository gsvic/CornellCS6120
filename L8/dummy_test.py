import json
import fileinput

from util import split_in_blocks, add_terminators
from lib import LoopPass

if __name__ == "__main__":
    input_json = ""
    for line in fileinput.input():
        input_json += line

    code = json.loads(input_json)

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

    print(json.dumps(code, indent=2))