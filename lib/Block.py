class Block:
    block_id = 0

    def __init__(self, instr_list):
        """
        The Block abstraction contains an instruction list
        of the input block
        :param instr_list: The instruction list
        """
        self._instr_list = instr_list
        self._name = None

        for instr in instr_list:
            if not self._name:
                if 'label' in instr:
                    self._name = instr['label']
                else:
                    self._name = "{}".format(Block.block_id)
                    Block.block_id += 1

    def get_definitions(self):
        """
        Extracts the definitions of the instruction list
        :return: The block definitions
        """
        definitions = []
        for instr in self._instr_list:
            if 'dest' in instr:
                definitions.append(instr['dest'])

        return definitions

    def get_uses(self):
        """
        Extracts all uses from the input block
        :return: The uses list
        """
        uses = []
        for instr in self._instr_list:
            if 'args' in instr:
                for arg in instr['args']:
                    uses.append(arg)
        return uses

    def get_block_name(self):
        """
        :return: The block name
        """
        return self._name

    def get_name(self):
        """
        :return: The block name
        """
        return self._name

    def get_instr_list(self):
        """
        :return: The instruction list
        """
        return self._instr_list

    def add_instr(self, instr):
        """
        Appends a new instruction to the instruction list
        :param instr: The new instruction
        :return: None
        """
        self._instr_list.append(instr)

    def __str__(self):
        return "Block[{}]".format(self._name)
