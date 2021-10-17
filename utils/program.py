import os
import subprocess
import sys
from typing import List
from utils.defs import TokenType, Token, OpType, Program, Op, Intrinsic
from utils.asm import initialize_asm, generate_asm, compile_asm, link_object_file
def intrinsic_exists(token: str) -> bool:
    if hasattr(Intrinsic, token):
        return True
    return False

def generate_program(tokens = List[Token]) -> Program:
    program = []
    for token in tokens:
        if token.type == TokenType.CHAR:
            op_type = OpType.PUSH_STR
        elif token.type == TokenType.INT:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.STR:
            op_type = OpType.PUSH_STR
        elif token.value.lower() == 'do':
            op_type = OpType.DO
        elif token.value.lower() == 'end':
            op_type = OpType.END
        elif token.value.lower() == 'if':
            op_type = OpType.IF
        elif token.value.lower() == 'elif':
            op_type = OpType.ELIF
        elif token.value.lower() == 'else':
            op_type = OpType.ELSE
        elif token.value.lower() == 'while':
            op_type = OpType.WHILE
        else:
            if intrinsic_exists(token.value.upper()):
                op_type = OpType.INTRINSIC
            else:
                raise AttributeError (f"Intrinsic '{token.value}' is not found")

        operand = Op(op_type, token)
        program.append(operand)
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