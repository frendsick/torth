from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple

STACK: List[str] = []

class Colors:
    FAIL    = '\033[91m'
    HEADER  = '\033[95m'
    NC      = '\033[0m'
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
    MEMORY=auto()
    WHILE=auto()

class Intrinsic(Enum):
    AND=auto()
    ARGC=auto()
    ARGV=auto()
    DIV=auto()
    DROP=auto()
    DUP=auto()
    ENVP=auto()
    EXIT=auto()
    EQ=auto()
    GE=auto()
    GT=auto()
    HERE=auto()
    INPUT=auto()
    LE=auto()
    LOAD=auto()
    LT=auto()
    MINUS=auto()
    MOD=auto()
    MUL=auto()
    NE=auto()
    NOT=auto()
    NTH=auto()
    OR=auto()
    OVER=auto()
    PLUS=auto()
    PRINT=auto()
    PUTS=auto()
    ROT=auto()
    STORE=auto()
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
    PUSH_HEX=auto()
    PUSH_INT=auto()
    PUSH_PTR=auto()
    PUSH_STR=auto()
    WHILE=auto()

class TokenType(Enum):
    ARRAY=auto()
    BOOL=auto()
    HEX=auto()
    INT=auto()
    KEYWORD=auto()
    PTR=auto()
    STR=auto()
    WORD=auto()

Location = Tuple[str, int, int]     # Source file name, row, column
Memory = Tuple[str, str, Location]  # Name, str(size), Location

@dataclass
class Token:
    value: str
    type: TokenType
    location: Location

# param types, return types
Signature   = Tuple[List[str], List[str]]

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
TYPE_REGEX: Dict[str, str] = {
    'INT': '-?\d+',
    'PTR': '\*ptr \S+',
    'STR': '\*buf s_\S+'
}
