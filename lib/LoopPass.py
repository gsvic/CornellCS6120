from lib import CFG
from .Block import Block

class LoopPass:
    def __init__(self, blocks):
        self.__blocks = blocks
        self.__cfg = CFG(blocks)

        self.__loops = self.__cfg.find_loops()

    def execute_pass(self):
        # Return if there are no loops
        if not self.__loops:
            return self.__blocks

        no_invariants = True
        for loop in self.__loops.values():
            loop.mark_invariants()
            no_invariants = no_invariants and not loop.has_invariants()

        # Return if there are no invariants in the loop
        if no_invariants:
            return self.__blocks

        blocks = list()

        prehead_idx = 0

        for block in self.__blocks:
            # Check if a loop starts here
            if block.get_name() in self.__loops:
                # We are inside a loop
                loop = self.__loops[block.get_name()]
                # If the loop has invariants, add a preheader block
                if loop.has_invariants():
                    preheader_block = loop.create_preheader_block()

                    # Check for jumps
                    last_blk_last_instr = blocks[-1].get_instr_list()[-1]
                    if "op" in last_blk_last_instr and "jmp" in last_blk_last_instr["op"]:
                        last_blk_last_instr["labels"][0] = preheader_block.get_name()

                    blocks.append(preheader_block)

            refined_block = list()
            # Check if the current instrument is not an invariant
            for inst in block.get_instr_list():
                if "invariant" not in inst:
                    refined_block.append(inst)

            blocks.append(Block(refined_block))

        return blocks

