import subprocess
from typing import List
from compiler.defs import TokenType, Token, OpType, Program, Op, Intrinsic

def intrinsic_exists(token: str) -> bool:
    return bool(hasattr(Intrinsic, token))

def generate_program(tokens = List[Token]) -> Program:
    program: List[Op] = []
    for id, token in enumerate(tokens):
        token_value: str = token.value.upper()
        if token.type == TokenType.ARRAY:
            op_type = OpType.PUSH_ARRAY
        elif token.type == TokenType.BOOL:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.CSTR:
            op_type = OpType.PUSH_CSTR
        elif token.type == TokenType.INT:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.STR:
            op_type = OpType.PUSH_STR
        elif token_value == 'BREAK':
            op_type = OpType.BREAK
        elif token_value == 'DO':
            op_type = OpType.DO
        elif token_value == 'END':
            op_type = OpType.END
        elif token_value == 'ENDIF':
            op_type = OpType.ENDIF
        elif token_value == 'IF':
            op_type = OpType.IF
        elif token_value == 'ELIF':
            op_type = OpType.ELIF
        elif token_value == 'ELSE':
            op_type = OpType.ELSE
        elif token_value == 'WHILE':
            op_type = OpType.WHILE
        elif intrinsic_exists(token_value):
            op_type = OpType.INTRINSIC
        else:
            raise AttributeError (f"Operation '{token.value}' is not found")

        operand: Op = Op(id, op_type, token)
        program.append(operand)
    return program

def run_code(exe_file: str) -> None:
    subprocess.run([f'./{exe_file}'])