import json
from collections import defaultdict
from copy import deepcopy

from lib import CFG
from util import split_in_blocks, add_terminators


class SSA:
    # A constant that defines an undefined value
    UNDEFINED = "_undef_"

    # Helper class Phi
    class Phi:
        def __init__(self, source_block, var_name):
            """
            Represents a Phi argument
            :param source_block: The source block
            :param var_name: The variable name
            """
            self.source_block = source_block
            self.var_name = var_name

        def __str__(self):
            return "Phi({}, {})".format(self.source_block, self.var_name)

    # Helper class PhiSet
    class PhiSet:
        def __init__(self, ssa, var_name, block_name):
            """
            Represents a set of Phi arguments for a given variable inside a block
            :param ssa: The SSA instance
            :param var_name: The variable name
            :param block_name: The block name
            """
            self.ssa = ssa
            self.block_name = block_name
            self.var_name = var_name
            self.phis = set()

        def add_phi(self, phi):
            self.phis.add(phi)

        def to_instr(self):
            return {
                "op": "phi",
                "labels": [d.source_block for d in self.phis],
                "args": [d.var_name for d in self.phis],
                "type": self.ssa.var_type[self.var_name],
                "dest": self.ssa.phi_dst[self.block_name][self.var_name]
            }

    def __init__(self, blocks, func):
        self.func = func
        self.blocks = blocks
        self.cfg = CFG(self.blocks)
        self.df = self.cfg.get_domination_frontiers()
        self.domtree = self.cfg.get_dom_tree()
        self.args = [arg["name"] for arg in func["args"]] if "args" in func else []

        # Map definitions to blocks
        self.def_to_blocks = self.__get_defs_to_blocks()

        # Get some metadata -- Initialize type per variable
        self.var_type = dict()

        if "args" in self.func:
            for arg in self.func["args"]:
                self.var_type[arg["name"]] = arg["type"]

        for block in blocks:
            for instr in block.get_instr_list():
                if "dest" in instr:
                    self.var_type[instr["dest"]] = instr["type"]

        # Extract phi-nodes
        self.phi_nodes = self.__init_phi_nodes()
        self.phi_sets = dict()

        # Keep track of phi destinations
        self.phi_dst = {blk.get_name(): {phi: None for phi in self.phi_nodes[blk]} for blk in self.blocks}

        # Initialize stack and counters per variable for renaming
        self.stack = defaultdict(list, {arg: [arg] for arg in self.args})
        self.counter2var = defaultdict(int)

        # Rename
        self.__rename(self.blocks[0])

    def _stack_push(self, var_name):
        """
        Pushes a variable name to the stack
        :param var_name: The variable name
        :return: The new name to be assigned
        """
        last_name = "{}.{}".format(var_name, self.counter2var[var_name])
        self.stack[var_name].insert(0, last_name)
        self.counter2var[var_name] += 1

        return last_name

    def _stack_peek(self, var_name):
        """
        Returns the first element of the stack of a given variable name
        :param var_name: The variable name
        :return: The first element in the stack
        """
        if not self.stack[var_name]:
            print()
        return self.stack[var_name][0]

    def __get_defs_to_blocks(self):
        """
        Maps definitions to lists of blocks, that is, the blocks in which the
        definition exists.
        :return: None
        """
        def_to_blocks = defaultdict(list)

        for block in self.blocks:
            for definition in block.get_definitions():
                def_to_blocks[definition.get_name()].append(block.get_name())

        return def_to_blocks

    def add_phi(self, dst_block, phi, src_block):
        """
        Adds a phi-argument to the destination block
        :param dst_block: The destination block
        :param phi: The phi argument
        :param src_block: The source block
        :return: None
        """
        if dst_block not in self.phi_sets:
            self.phi_sets[dst_block] = dict()
        if phi not in self.phi_sets[dst_block]:
            self.phi_sets[dst_block][phi] = SSA.PhiSet(self, var_name=phi, block_name=dst_block)

        self.phi_sets[dst_block][phi].add_phi(SSA.Phi(src_block.get_block_name(), self._stack_peek(phi)))

    def add_undef_phi(self, dst_block, phi, src_block):
        """
        Adds an undefined phi-argument to the destination block
        :param dst_block: The destination block
        :param phi: The phi argument
        :param src_block: The source block
        :return: None
        """
        if dst_block not in self.phi_sets:
            self.phi_sets[dst_block] = dict()
        if phi not in self.phi_sets[dst_block]:
            self.phi_sets[dst_block][phi] = SSA.PhiSet(self, var_name=phi, block_name=dst_block)

        self.phi_sets[dst_block][phi].add_phi(SSA.Phi(src_block.get_block_name(), SSA.UNDEFINED))

    def __rename(self, block):
        tmp = deepcopy(self.stack)

        for phi in self.phi_nodes[block.get_name()]:
            self.phi_dst[block.get_name()][phi] = self._stack_push(phi)

        print(block.get_name())
        for instr in block.get_instr_list():
            if "args" in instr:
                instr["args"] = [self._stack_peek(v) for v in instr["args"]]

            if "dest" in instr:
                instr["dest"] = self._stack_push(instr["dest"])

        # Get successors
        successors = self.cfg.get_nodes()[block.get_name()].get_successors()

        for s in successors:
            for phi in self.phi_nodes[s]:
                if phi in self.stack:
                    self.add_phi(s, phi, block)
                else:
                    self.add_undef_phi(s, phi, block)

        dominated = self.domtree[block.get_name()]

        for d in sorted(dominated):
            self.__rename(self.cfg.get_nodes()[d].get_block())

        self.stack.clear()
        self.stack.update(tmp)

    def __init_phi_nodes(self):
        """
        Initializes the phi nodes
        :return:
        """
        phi2blocks = defaultdict(list)

        for var in self.def_to_blocks:
            for block in self.def_to_blocks[var]:
                block_df = self.df[block]

                for b in block_df:
                    # Add a phi-node
                    if var not in phi2blocks[b]:
                        phi2blocks[b].append(var)

                    if b not in self.def_to_blocks[var]:
                        self.def_to_blocks[var].append(b)

        return phi2blocks


def do_ssa(code):
    """
    Apply SSA to the given code
    :param code: The code, in JSON format
    :return: The new code, including the phi arguments
    """
    new_instrs = []

    for func in code["functions"]:
        # Init blocks
        blocks = split_in_blocks(func)
        blocks = add_terminators(blocks)

        ssa = SSA(blocks, func)

        for block in blocks:
            blk_name = block.get_name()
            block_instrs = block.get_instr_list()

            if blk_name in ssa.phi_sets:
                phi_instr = [phi.to_instr() for phi in ssa.phi_sets[blk_name].values()]

                # Add the label instruction first
                if "label" in block_instrs[0]:
                    for pi in phi_instr:
                        block_instrs.insert(1, pi)
                else:
                    for pi in phi_instr:
                        block_instrs.insert(0, pi)

            for instr in block_instrs:
                new_instrs.append(instr)

            func["instructions"] = new_instrs

        return code