"""
Definitions for classes, constants, and types used by the Torth compiler
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple

STACK: List[str] = []
COLORS: Dict[str, str] = {
    'FAIL'      : '\033[91m',
    'HEADER'    : '\033[95m',
    'NC'        : '\033[0m',
    'WARNING'   : '\033[93m'
}

class Keyword(Enum):
    """Available keywords in the Torth language"""
    BREAK=auto()
    CONST=auto()
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
    """Available intrinsics in the Torth language"""
    AND=auto()
    ARGC=auto()
    ARGV=auto()
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
    LOAD_BYTE=auto()
    LOAD_QWORD=auto()
    LT=auto()
    MINUS=auto()
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
    STORE_BYTE=auto()
    STORE_QWORD=auto()
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
    """Available operand types in the Torth language"""
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
    PUSH_CHAR=auto()
    PUSH_HEX=auto()
    PUSH_INT=auto()
    PUSH_PTR=auto()
    PUSH_STR=auto()
    WHILE=auto()

class TokenType(Enum):
    """Available Types for Token objects"""
    ARRAY=auto()
    BOOL=auto()
    CHAR=auto()
    HEX=auto()
    INT=auto()
    KEYWORD=auto()
    PTR=auto()
    STR=auto()
    WORD=auto()

Location    = Tuple[str, int, int]      # Source file name, row, column
Memory      = Tuple[str, str, Location] # Name, str(size), Location

@dataclass
class Constant:
    """CONST keyword can be used to create a named immutable integer value"""
    name: str
    value: str
    location: Location

@dataclass
class Token:
    """Tokens are words from a program that translates to certain operands"""
    value: str
    type: TokenType
    location: Location

# param types, return types
Signature   = Tuple[List[str], List[str]]

@dataclass
class Function:
    """Functions are reusable named sequences of Token objects"""
    name: str
    signature: Signature
    tokens: List[Token]

@dataclass
class Op:
    """Operands stores Token's information which is used in assembly code generation"""
    id: int
    type: OpType
    token: Token

Program = List[Op]
TYPE_REGEX: Dict[str, str] = {
    'INT': r'-?\d+',
    'PTR': r'\*ptr \S+',
    'STR': r'\*buf s_\S+'
}
