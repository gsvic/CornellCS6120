from .BlockCFGNode import BlockCFGNode


class CFG:
    def __init__(self, block_list):
        """
        The CFG class represents the Control-Flow-Graph of the given block list
        :param block_list: The block list
        """
        self.nodes = {}

        # Instantiate a BlockCFGNode per block
        for block in block_list:
            self.nodes[block.get_block_name()] = BlockCFGNode(block)

        # Create the edges
        for block in block_list:
            for instr in block.get_instr_list():
                if 'op' in instr and instr['op'] in {'jmp', 'br'}:
                    for label in instr['labels']:
                        if label != block.get_block_name():
                            self.nodes[block.get_block_name()].add_successor(self.nodes[label])
                            self.nodes[label].add_predecessor(self.nodes[block.get_block_name()])