from dataclasses import dataclass
from enum import Enum, auto
from typing import List,Tuple
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