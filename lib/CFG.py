from .BlockCFGNode import BlockCFGNode

from collections import defaultdict


class CFG:
    def __init__(self, block_list):
        """
        The CFG class represents the Control-Flow-Graph of the given block list
        :param block_list: The block list
        """
        self.nodes = {}

        # Keeps a global definition state (last annotation, or, id)
        self.__annotations = {}

        # Instantiate a BlockCFGNode per block
        for block in block_list:
            # Get the current definitions and annotate them
            annotated_defs = self.__annotate_definitions(block.get_definitions())
            self.nodes[block.get_block_name()] = BlockCFGNode(block, annotated_defs)

        # Create the edges
        self.__set_graph_edges(block_list)

    def switch_directions(self):
        """
        Switch directions in every node in the graph
        :return: None
        """
        for node in self.nodes.items():
            node[1].switch_direction()

    def __set_graph_edges(self, block_list):
        """
        Given a block list, it sets the edges between the BlockCFGNodes
        :param block_list: The block list
        :return: None
        """
        for block in block_list:
            for instr in block.get_instr_list():
                if 'op' in instr and instr['op'] in {'jmp', 'br'}:
                    for label in instr['labels']:
                        self.nodes[block.get_block_name()].add_successor(self.nodes[label])
                        self.nodes[label].add_predecessor(self.nodes[block.get_block_name()])

    def __annotate_definitions(self, defs):
        """
        Annotates the input definitions
        :param defs:
        :return:
        """
        annotated_defs = {}
        for d in defs:
            if d not in self.__annotations:
                self.__annotations[d] = 0
            else:
                self.__annotations[d] += 1

            annotated_defs[d] = self.__annotations[d]

        return annotated_defs
