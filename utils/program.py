import os
import subprocess
import sys
from typing import List
from utils.defs import TokenType, Token, OpType, Program, Op, Intrinsic
from utils.asm import get_op_asm, initialize_asm, generate_asm, compile_asm, link_object_file
def intrinsic_exists(token: str) -> bool:
    if hasattr(Intrinsic, token):
        return True
    return False

def generate_program(tokens = List[Token]) -> Program:
    program = []
    id=0
    for token in tokens:
        token_value = token.value.upper()
        if token.type == TokenType.BOOL:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.CHAR:
            op_type = OpType.PUSH_STR
        elif token.type == TokenType.INT:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.STR:
            op_type = OpType.PUSH_STR
        elif token_value == 'DO':
            op_type = OpType.DO
        elif token_value == 'END':
            op_type = OpType.END
        elif token_value == 'IF':
            op_type = OpType.IF
        elif token_value == 'ELIF':
            op_type = OpType.ELIF
        elif token_value == 'ELSE':
            op_type = OpType.ELSE
        elif token_value == 'WHILE':
            op_type = OpType.WHILE
        else:
            if intrinsic_exists(token_value):
                op_type = OpType.INTRINSIC
            else:
                raise AttributeError (f"Intrinsic '{token.value}' is not found")

        operand = Op(id, op_type, token)

        op_size = (len(get_op_asm(operand).split('\n')) - 1) * 8 # 64bit = 8bytes
        operand.size = op_size

        program.append(operand)
        id += 1
    return program

def compile_code(tokens = List[Token]) -> None:
    asm_file = f"output/{os.path.basename(sys.argv[1]).replace('.torth', '.asm')}"
    program = generate_program(tokens)
    initialize_asm(asm_file)
    generate_asm(program, asm_file)
    compile_asm(asm_file)
    link_object_file(asm_file.replace('.asm', '.o'))

def run_code(exe_file: str) -> None:
    subprocess.run([f'output/{exe_file}'])