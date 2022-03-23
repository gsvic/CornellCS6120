from .Definition import Definition

class Block:
    block_id = 1
    var_id = 1

    def __init__(self, instr_list):
        """
        The Block abstraction contains an instruction list
        of the input block
        :param instr_list: The instruction list
        """
        self._instr_list = instr_list
        self._name = None
        self.definitions = []

        for instr in instr_list:
            if not self._name:
                if 'label' in instr:
                    self._name = instr['label']
                else:
                    self._name = "b{}".format(Block.block_id)
                    Block.block_id += 1

        self.set_instructions(instr_list)

    def set_instructions(self, instr_list):
        self.definitions = []

        for instr in instr_list:
            if 'dest' in instr:
                name = instr['dest']
                value = "?"
                uid = Block.var_id
                Block.var_id += 1

                if 'value' in instr:
                    value = instr['value']

                self.definitions.append(Definition(name, value, uid))

        self._instr_list = instr_list

    def get_definitions(self):
        return self.definitions

    def get_definition_names(self):
        """
        Extracts the definitions of the instruction list
        :return: The block definitions
        """
        definitions = []
        for instr in self._instr_list:
            if 'dest' in instr:
                definitions.append(instr['dest'])

        return definitions

    def get_full_definitions(self):
        """
        Extracts the definitions of the instruction list, along with their values
        :return: The block definitions
        """
        definitions = dict()
        for instr in self._instr_list:
            if 'dest' in instr:
                if 'value' in instr:
                    definitions[instr['dest']] = instr['value']
                else:
                    definitions[instr['dest']] = "?"

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

    @staticmethod
    def create_entry_block(idx, next_block):
        instr = [
            {'label': 'entry%s' % idx},
            {'jmp': next_block}
        ]

        return Block(instr)

