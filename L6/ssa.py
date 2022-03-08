from collections import defaultdict
from pybril import PyBril
from lib import CFG
from util import split_in_blocks, add_terminators


class SSA:
    # A constant that defines an undefined value
    UNDEFINED = "_undef_"

    def __init__(self, blocks, args):
        self.blocks = blocks
        self.cfg = CFG(self.blocks)
        self.df = self.cfg.get_domination_frontiers()
        self.domtree = self.cfg.get_immediate_dominators()
        self.args = args

        # Map definitions to blocks
        self.def_to_blocks = self.__get_defs_to_blocks()

        # Extract phi-nodes
        self.phi_nodes = self.__init_phi_nodes()
        self.phi_args = defaultdict(lambda: defaultdict(list))

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
        self.phi_args[dst_block][phi].append(Phi(src_block.get_block_name(), self._stack_peek(phi)))

    def add_undef_phi(self, dst_block, phi, src_block):
        """
        Adds an undefined phi-argument to the destination block
        :param dst_block: The destination block
        :param phi: The phi argument
        :param src_block: The source block
        :return: None
        """
        self.phi_args[dst_block][phi].append(Phi(src_block.get_block_name(), SSA.UNDEFINED))

    def __rename(self, block):
        tmp = {var[0]: var[1] for var in self.stack.items()}

        for instr in block.get_instr_list():
            if "args" in instr:
                instr["args"] = [self._stack_peek(v) for v in instr["args"]]

            if "dest" in instr:
                instr["dest"] = [self._stack_push(v) for v in instr["dest"]]

        # Get successors
        successors = self.cfg.get_nodes()[block.get_name()].get_successors()

        for s in successors:
            for phi in self.phi_nodes[s]:
                if phi in self.stack:
                    self.add_phi(s, phi, block)
                else:
                    self.add_undef_phi(s, phi, block)

        dominated = self.domtree[block.get_name()]
        for d in dominated:
            self.__rename(self.cfg.get_nodes()[d].get_block())

        self.stack.clear()
        self.stack.update(tmp)

    def __init_phi_nodes(self):
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


class Phi():
    """
    Represents a Phi argument
    """
    def __init__(self, source_block, var_name):
        self.source_block = source_block
        self.var_name = var_name

    def __str__(self):
        return "Phi({}, {})".format(self.source_block, self.var_name)


if __name__ == "__main__":
    BRIL_BINARIES = "/Users/victorgiannakouris/Dev/bril/.venv/bin"
    some_bril = "./ssa.bril"
    brilpy = PyBril(bril_binaries_path=BRIL_BINARIES)
    code = brilpy.bril2json(some_bril)

    for func in code["functions"]:
        # Init blocks
        blocks = split_in_blocks(func)
        blocks = add_terminators(blocks)

        ssa = SSA(blocks, [arg["name"] for arg in func["args"]])

        print()