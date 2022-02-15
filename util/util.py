from lib import Block


def split_in_blocks(input):
    """
    Splits the input set of instructions into blocks
    :param input: The set of instructions
    :return: A list of blocks
    """
    blocks = []
    current_block_instr = []

    for instr in input['instrs']:
        if 'label' in instr:
            blocks.append(Block(current_block_instr))
            current_block_instr = []

        current_block_instr.append(instr)

    if current_block_instr:
        blocks.append(Block(current_block_instr))

    return blocks