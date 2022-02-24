from .BlockCFGNode import BlockCFGNode
from .Block import Block

import functools

class CFG:
    def __init__(self, block_list, add_entry_block=True):
        """
        The CFG class represents the Control-Flow-Graph of the given block list
        :param block_list: The block list
        """
        self.nodes = {}

        # Keeps a global definition state (last annotation, or, id)
        self.__annotations = {}

        self.__entry_id = 1

        # Instantiate a BlockCFGNode per block
        for block in block_list:
            # Get the current definitions and annotate them
            annotated_defs = self.__annotate_definitions(block.get_definitions())
            self.nodes[block.get_block_name()] = BlockCFGNode(block, annotated_defs)

        # Create the edges
        self.__set_graph_edges(block_list)

        # Check if an entry block is required
        if add_entry_block:
            self.add_entry_block()

        # Compute dominators lazily, upon request. Then cache the result (see get_dominators() method)
        self.dominators = None

    def add_entry_block(self):
        first_node = list(self.nodes.items())[0][1]
        if len(first_node.get_predecessors()) > 0:
            entry_block = Block.create_entry_block(self.get_next_entry_idx(), first_node.get_name())
            entry_node = BlockCFGNode(entry_block, self.__annotate_definitions(entry_block.get_definitions()))
            first_node.add_predecessor(entry_node)
            new_nodes = {entry_node.get_name(): entry_node}
            new_nodes.update(self.nodes)
            self.nodes = new_nodes

    def get_next_entry_idx(self):
        idx = self.__entry_id
        self.__entry_id += 1

        return idx

    def get_nodes(self):
        return self.nodes

    def switch_directions(self):
        """
        Switch directions in every node in the graph
        :return: None
        """
        for node in self.nodes.items():
            node[1].switch_direction()

    def get_dominators(self):
        """
        Returns the a dict with the dominators per node
        :return: The dominators dict
        """
        if self.dominators:
            return self.dominators

        nodes = list(self.get_nodes().items())

        dom = {name: set(self.nodes) for name in self.nodes}

        changed = True

        while changed:
            for name, node in nodes:
                preds = [dom[pred] for pred in node.get_predecessors()]

                if preds:
                    preds = list(functools.reduce(lambda x, y: x.intersection(y), preds))

                result = {name}.union(preds)

                changed = dom[name] != result

                if changed:
                    dom[name] = result

        for d in dom:
            dom[d] = list(dom[d])

        self.dominators = dom

        return dom

    def get_immediate_dominators(self):
        """
        Returns a dict with the immediate dominatees of each node.
        :return: The immediate dominators dict
        """

        # 1. Get the dominators
        dominators = self.get_dominators()

        # 2. Init an empty list per node
        immediate_dominators = {node: list() for node in self.nodes}

        for node in self.nodes:
            node_dominators = dominators[node]

            for nd in node_dominators:
                preds = self.nodes[node].get_predecessors()

                # If the dominator (nd) is a direct predecessor of the node,
                # add the node to the nd`s immediate dominantees list.
                if nd in preds:
                    immediate_dominators[nd].append(node)

        return immediate_dominators

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
