from dataclasses import dataclass
from enum import Enum, auto
from typing import List,Tuple

MEMORY_SIZE     = 8000
INCLUDE_PATHS   = ['./', './lib/']

class Colors:
    FAIL = '\033[91m'
    HEADER = '\033[95m'
    NC = '\033[0m'
    WARNING = '\033[93m'

class Keyword(Enum):
    DO=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    ENDIF=auto()
    IF=auto()
    INCLUDE=auto()
    FUNC=auto()
    WHILE=auto()

class Intrinsic(Enum):
    AND=auto()
    ARGC=auto()
    ARGV=auto()
    CAST_BOOL=auto()
    CAST_INT=auto()
    CAST_PTR=auto()
    GET_NTH=auto()
    DIV=auto()
    DIVMOD=auto()
    DROP=auto()
    DUP=auto()
    ENVP=auto()
    EQ=auto()
    GE=auto()
    GT=auto()
    HERE=auto()
    INPUT=auto()
    LE=auto()
    LT=auto()
    MINUS=auto()
    MOD=auto()
    MUL=auto()
    NE=auto()
    NOT=auto()
    OR=auto()
    OVER=auto()
    PLUS=auto()
    PUTS=auto()
    PRINT=auto()
    PRINT_INT=auto()
    ROT=auto()
    SWAP=auto()
    SWAP2=auto()
    SYSCALL0=auto()
    SYSCALL1=auto()
    SYSCALL2=auto()
    SYSCALL3=auto()
    SYSCALL4=auto()
    SYSCALL5=auto()
    SYSCALL6=auto()

class OpType(Enum):
    DO=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    ENDIF=auto()
    IF=auto()
    INTRINSIC=auto()
    PUSH_ARRAY=auto()
    PUSH_CSTR=auto()
    PUSH_INT=auto()
    PUSH_STR=auto()
    WHILE=auto()

class TokenType(Enum):
    ARRAY=auto()
    BOOL=auto()
    CHAR=auto()
    CSTR=auto()
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
    id: int
    type: OpType
    token: Token

Program=List[Op]

@dataclass
class Func:
    id: int
    name: str
    ops: Program

STACK=[]
REGEX={'INT': '-?\d+', '*buf': '\*buf \S+'}
