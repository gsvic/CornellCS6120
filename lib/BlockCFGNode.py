class BlockCFGNode:
    def __init__(self, block):
        """
        The BlockCFGNode class represents a node of the CFG graph
        that connects the blocks.
        :param block: The Block instance
        """
        self._block = block
        self._predecessors = {}
        self._successors = {}

    def add_predecessor(self, predecessor):
        """
        Adds a predecessor to the node
        :param predecessor: The predecessor
        :return: None
        """
        self._predecessors[predecessor.get_name()] = predecessor

    def add_successor(self, successor):
        """
        Adds a successor to the node
        :param successor: The successor
        :return: None
        """
        self._successors[successor.get_name()] = successor

    def has_successor(self, successor_name):
        """
        Checks if the node has a specific successor
        :param successor_name: The successor's name
        :return: True if the current node contains the successor, False otherwise
        """
        return successor_name in self._successors

    def get_block(self):
        """
        Retrieves the Block instance of the BlockCFGNode
        :return: The Block instance
        """
        return self._block

    def get_predecessors(self):
        """
        Getter method for the predecessors
        :return: A list containing the predecessors
        """
        return self._predecessors

    def get_successors(self):
        """
        Getter method for the successors
        :return: A list containing the successors
        """
        return self._successors

    def get_name(self):
        """
        Getter method for the block name
        :return: The block name
        """
        return self._block.get_block_name()

    def get_inputs(self):
        """
        Retrieves the input definitions of the node
        :return: The inpput definitions
        """
        return self._get_inputs(set())

    def _get_inputs(self, seen):
        """
        Retrieves the input definitions of the node
        :param seen: The nodes (blocks) seen so far, to avoid cycles
        :return: The input definition set
        """
        inputs = set()
        for predecessor in self._predecessors.values():
            if predecessor.get_name() not in seen:
                seen.add(predecessor.get_name())
                predecessor_out = predecessor.get_outputs(seen)
                for d in predecessor_out:
                    inputs.add(d)

        return inputs

    def get_outputs(self, seen):
        """
        Retrieves the outputs of the node
        :param seen: The nodes (blocks) seen so far, to avoid cycles
        :return: The output definitions set
        """
        outputs = self._get_inputs(seen)

        for d in self._block.get_definitions():
            outputs.add(d)

        return outputs

    def __str__(self):
        return "BlockCFGNode[block_name={}]".format(self._block.get_block_name())
