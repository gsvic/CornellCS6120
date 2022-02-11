def split_in_blocks(input):
    """
    Splits the input set of instructions into blocks
    :param input: The set of instructions
    :return: A list of blocks
    """
    blocks = []
    current_block = []

    for instr in input['instrs']:
        current_block.append(instr)
        if 'op' in instr and instr['op'] in {'br', 'jmp'}:
            blocks.append(current_block)
            current_block = []

    if current_block:
        blocks.append(current_block)

    return blocks