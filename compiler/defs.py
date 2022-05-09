from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class Colors:
    FAIL = '\033[91m'
    HEADER = '\033[95m'
    NC = '\033[0m'
    WARNING = '\033[93m'

class Keyword(Enum):
    BREAK=auto()
    DO=auto()
    DONE=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    ENDIF=auto()
    FUNCTION=auto()
    IF=auto()
    WHILE=auto()

class Intrinsic(Enum):
    AND=auto()
    ARGC=auto()
    ARGV=auto()
    CAST_BOOL=auto()
    CAST_INT=auto()
    CAST_PTR=auto()
    DIV=auto()
    DIVMOD=auto()
    DROP=auto()
    DUP=auto()
    DUP2=auto()
    ENVP=auto()
    EXIT=auto()
    EQ=auto()
    GE=auto()
    GET_NTH=auto()
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
    BREAK=auto()
    DO=auto()
    DONE=auto()
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
Location = tuple[str, int, int]

@dataclass
class Token:
    value: str
    type: TokenType
    location: Location

# param types, return types
Signature   = tuple[List[str], List[str]]

@dataclass
class Function:
    name: str
    signature: Signature
    tokens: List[Token]

@dataclass
class Op:
    id: int
    type: OpType
    token: Token

Program = List[Op]

STACK: List[str] = []
REGEX: Dict[str, str] = {'INT': '-?\d+', '*buf': '\*buf \S+'}
