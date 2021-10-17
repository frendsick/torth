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
    STR=auto()
    WORD=auto()

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
    print(sys.argv[1], os.path.isfile(sys.argv[1]))
    if os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    raise FileNotFoundError("Argument '" + sys.argv[1] + "' is not a file")

def get_token_type(token_text: str) -> TokenType:
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
    
    # Get all newline characters and tokens with their locations from the code
    newline_indexes = [i for i in range(len(code)) if code[i] == '\n']
    # Strings are between quotes and can contain whitespaces
    token_matches = [token for token in re.finditer(r'".*"|\S+', code)]

    tokens = []
    for match in token_matches:
        value     = match.group(0)
        type      = get_token_type(value)
        location  = get_token_location(os.path.basename(code_file), match.start()+1, newline_indexes)
        token     = Token(value, type, location)
        tokens.append(token)

    return tokens

def compile_code(tokens = List[Token]) -> Program:
    raise NotImplementedError("Function '" +  compile_code.__name__ + "' is not implemented")

def main():
    code_file = get_code_file_from_arguments()
    tokens = get_tokens_from_code(code_file)
    compile_code(tokens)
    raise NotImplementedError("Function '" +  main.__name__ + "' is under development")

if __name__ == "__main__":
    main()