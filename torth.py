#!/usr/bin/env python3
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

class Keyword(Enum):
    DO=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    IF=auto()
    INCLUDE=auto()
    MACRO=auto()
    WHILE=auto()

class Intrinsic(Enum):
    AND=auto()
    ARGC=auto()
    ARGV=auto()
    CAST_BOOL=auto()
    CAST_INT=auto()
    CAST_PTR=auto()
    DIVMOD=auto()
    DROP=auto()
    DUP=auto()
    EQ=auto()
    GE=auto()
    GT=auto()
    HERE=auto()
    LE=auto()
    LOAD8=auto()
    LOAD32=auto()
    LOAD64=auto()
    LT=auto()
    MEM=auto()
    MINUS=auto()
    MUL=auto()
    NE=auto()
    NOT=auto()
    OR=auto()
    OVER=auto()
    PLUS=auto()
    PRINT=auto()
    PRINT_INT=auto()
    ROT=auto()
    SHL=auto()
    SHR=auto()
    STORE8=auto()
    STORE32=auto()
    STORE64=auto()
    SWAP=auto()
    SYSCALL0=auto()
    SYSCALL1=auto()
    SYSCALL2=auto()
    SYSCALL3=auto()

class OpType(Enum):
    DO=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    IF=auto()
    INTRINSIC=auto()
    PUSH_INT=auto()
    PUSH_STR=auto()
    WHILE=auto()

class TokenType(Enum):
    CHAR=auto()
    INT=auto()
    KEYWORD=auto()
    STR=auto()
    WORD=auto()

# Source file name, row, column
Location=Tuple[str, int, int]

@dataclass
class Token:
    value: str
    type: TokenType
    location: Location

@dataclass
class Op:
    type: OpType
    token: Token

Program=List[Op]

def usage() -> None:
    print("Usage: ./torth.py file")
    exit(1)

def get_code_file_from_arguments() -> str:
    if len(sys.argv) != 2:
        usage()
    if os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    raise FileNotFoundError("Argument '" + sys.argv[1] + "' is not a file")

# Returns the Intrinsic class value from token
def get_token_value(token: str) -> str:
    if token.upper() == 'MOD':
        return 'DIVMOD'
    if token == '=':
        return 'EQ'
    if token == '>=':
        return 'GE'
    if token == '>':
        return 'GT'
    if token == '<=':
        return 'LE'
    if token == '<':
        return 'LT'
    if token == '-':
        return 'MINUS'
    if token == '*':
        return 'MUL'
    if token == '!=':
        return 'NE'
    if token == '+':
        return 'PLUS'
    if token == '.':
        return 'PRINT_INT'
    return token

def get_token_type(token_text: str) -> TokenType:
    keywords = ['do', 'elif', 'else', 'end', 'if', 'include', 'macro', 'while']
    # Check if all keywords are taken into account
    assert len(Keyword) == len(keywords) , f"Wrong number of keywords in get_token_type function! Expected {len(Keyword)}, got {len(keywords)}"

    # Keywords are case insensitive
    if token_text.lower() in keywords:
        return TokenType.KEYWORD
    if token_text[0] == token_text[-1] == '"':
        return TokenType.STR
    if token_text[0] == token_text[-1] == "'" and len(token_text) == 3:
        return TokenType.CHAR
    if token_text[0] == token_text[-1] == "'" and len(token_text) != 3:
        raise TypeError("Token " + token_text + " is not a CHAR. Please use double quotes (\"\") for string literals")
    try:
        _integer = int(token_text)
        return TokenType.INT
    except ValueError:
        return TokenType.WORD

# Returns tuple containing the row and the column where the token was found
def get_token_location(filename: str, position: int, newline_indexes: List[int]) -> Location:
    col = position
    row = 1
    for i in range(len(newline_indexes)):
        if i > 0:
            col = position - newline_indexes[i-1] - 1
            row +=1
        if newline_indexes[i] > position:
            return (filename, row, col)
    
    if len(newline_indexes) >= 1:
        row += 1
        col = position - newline_indexes[-1] - 1
    return (filename, row, col)

def get_tokens_from_code(code_file: str) -> List[Token]:
    with open(code_file, 'r') as f:
        code = f.read()
    
    # Remove all comments from the code
    code = re.sub(r'\s*\/\/.*', '', code)

    # Get all newline characters and tokens with their locations from the code
    newline_indexes = [i for i in range(len(code)) if code[i] == '\n']

    # Strings are between quotes and can contain whitespaces
    token_matches = [token for token in re.finditer(r'".*"|\S+', code)]

    tokens = []
    for match in token_matches:
        value     = get_token_value(match.group(0))
        type      = get_token_type(value)
        location  = get_token_location(os.path.basename(code_file), match.start()+1, newline_indexes)
        token     = Token(value, type, location)
        tokens.append(token)
    return tokens

def PUSH_STR(char: str) -> None:
    raise NotImplementedError("Function 'PUSH_STR' is not implemented")

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
                raise AttributeError ("Intrinsic '" + token.value + "' is not found")


        operand = Op(op_type, token)
        program.append(operand)
    return program

def initialize_asm(asm_file: str) -> None:
    default_asm = '''default rel
extern printf

section .rodata
  formatStrInt db "%d",10,0

section .bss
  int: RESQ 1 ; allocates 8 bytes

section .text
PrintInt:
  mov rsi, [rsp+8]
  mov rdi, formatStrInt
  mov rax, 0

  call printf
  ret

global main
main:
'''
    with open(asm_file, 'w') as f:
        f.write(default_asm)

def get_op_comment_asm(op: Op, op_type: OpType) -> str:
    src_file    = op.token.location[0]
    row         = str(op.token.location[1])
    col         = str(op.token.location[2])
    op_name     = op_type.name
    if op_name == "INTRINSIC":
        op_name = op_type.name + " " + op.token.value
    return ';; -- ' + op_name + ' | File: ' + src_file + ', Row: ' + row + ', Col: ' + col + '\n'

def generate_asm(program: Program, asm_file: str) -> None:
    asm_file = sys.argv[1].replace('.torth', '.asm')
    with open (asm_file, 'a') as f:
        for op in program:
            if op.type == OpType.PUSH_INT:
                f.write(get_op_comment_asm(op, op.type))
                f.write(f'  mov rax, {op.token.value}\n')
                f.write(f'  push rax\n')
            elif op.type == OpType.INTRINSIC:
                intrinsic = op.token.value.upper()
                if intrinsic == "PLUS":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  add rax, rbx\n')
                    f.write( '  push rax\n')
                elif intrinsic == "PRINT_INT":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write(f'  mov rsi, {op.type.value}\n')
                    f.write( '  mov [int], rsi\n')
                    f.write( '  call PrintInt\n')
                else:
                    raise NotImplementedError(f"Intrinsic '{op.token.value}' is not implemented")
            else:
                raise NotImplementedError(f"Operand '{op.type}' is not implemented")

        # Add exit syscall to asm_file
        f.write( '; -- exit syscall\n')
        f.write( '  mov rax, 0x1\n')
        f.write( '  xor rbx, rbx\n')
        f.write( '  int 0x80\n')

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{obj_file.replace(".o", "")}', obj_file])

def compile_code(tokens = List[Token]) -> None:
    asm_file = sys.argv[1].replace('.torth', '.asm')
    program = generate_program(tokens)
    initialize_asm(asm_file)
    generate_asm(program, asm_file)
    compile_asm(asm_file)
    link_object_file(asm_file.replace('.asm', '.o'))

def run_code(exe_file: str) -> None:
    subprocess.run([f'./{exe_file}'])

def main():
    code_file = get_code_file_from_arguments()
    tokens = get_tokens_from_code(code_file)
    compile_code(tokens)
    run_code(code_file.replace(".torth", ""))

if __name__ == "__main__":
    main()