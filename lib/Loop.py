from .Block import Block


class Loop:
    """
    The Loop class
    -- Contains the blocks that constitute the loop
    -- Some functionality is provided for identifying invariant instructions that can be moved-out of the loop
    -- A pre-header block can be created by invoking the create_preheader_block() method
    """
    PREHEAD_IDX = 0

    def __init__(self, blocks):
        self.__blocks = blocks
        self.__definitions = None
        self.__invariants = list()
        self.__preheader_block = None

    def get_all_definitions(self, var_name):
        """
        Collects all definitions of a specific var-name, of all blocks in the loop
        :return: The definitions
        """
        definitions = list()
        for block in self.__blocks:
            for inst in block.get_instr_list():
                if "dest" in inst:
                    dst = inst["dest"]
                    if dst == var_name:
                        definitions.append((var_name, inst))
        return definitions


    def is_loop_invariant(self, instr):
        """
        Checks if an instruction is loop-invariant
        :param instr: The instruction
        :return: True if the instruction is loop-invariant, false otherwise
        """

        # Check if all of the arguments are not reassigned (defined) inside the loop
        for arg in instr["args"]:
            matching_definitions = self.get_all_definitions(arg)

            # We're safe
            if not matching_definitions:
                continue

            # There is only one matching definition and it's invariant
            if len(matching_definitions) == 1:
                if "invariant" not in matching_definitions[0][1]:
                    return False
            elif len(matching_definitions) > 1:
                return False

        return True

    def mark_invariants(self):
        """
        Marks invariant instructions
        :return: None
        """
        changed = True

        while changed:
            changed = False

            for block in self.__blocks:
                for instr in block.get_instr_list():
                    # Check if instr is already marked
                    if "invariant" in instr:
                        continue

                    if "dest" in instr and "args" in instr and self.is_loop_invariant(instr):
                        instr["invariant"] = True
                        self.__invariants.append(instr)
                        changed = True

    def create_preheader_block(self):
        """
        Creates the pre-header block which includes all
        the loop-invariant instructions
        :return: The pre-header block
        """
        invariants = self.get_invariants()
        preheader_blk_name = "prehead{}".format(Loop.PREHEAD_IDX)
        invariants.insert(0, {"label": preheader_blk_name})
        Loop.PREHEAD_IDX += 1

        return Block(invariants)

    def has_invariants(self):
        """
        Checks if this loop has invariants
        :return: True if the loop has invariants, false otherwise
        """
        return len(self.__invariants) > 0

    def get_invariants(self):
        """
        Getter method for the invariant instructions
        :return: The loop-invariant instructions
        """
        return self.__invariants

    def get_blocks(self):
        """
        Gets the blocks inside a loop
        :return: The blocks in the loop
        """
        return self.__blocks

    def __str__(self):
        return "Loop [start={} -- end={}]".format(self.__blocks[0].get_name(), self.__blocks[-1].get_name())