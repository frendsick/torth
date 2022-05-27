"""
Definitions for classes, constants, and types used by the Torth compiler
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple, Union

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
    LOAD_BOOL=auto()
    LOAD_CHAR=auto()
    LOAD_INT=auto()
    LOAD_PTR=auto()
    LOAD_STR=auto()
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
    STORE_BOOL=auto()
    STORE_CHAR=auto()
    STORE_INT=auto()
    STORE_PTR=auto()
    STORE_STR=auto()
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
    PUSH_BOOL=auto()
    PUSH_CHAR=auto()
    PUSH_INT=auto()
    PUSH_PTR=auto()
    PUSH_STR=auto()
    WHILE=auto()

class TokenType(Enum):
    """Available Types for Token objects"""
    ANY=auto()
    BOOL=auto()
    CHAR=auto()
    INT=auto()
    KEYWORD=auto()
    PTR=auto()
    STR=auto()
    WORD=auto()

@dataclass
class TypeNode:
    """Node for TypeStack linked list containing the current Token's type"""
    value: TokenType
    next_node: Union[TypeNode, None] = None

class TypeStack:
    """Linked list containing the types on the virtual stack used in type checking"""
    def __init__(self) -> None:
        self.head: Union[TypeNode, None] = None

    def print(self):
        """Print the contents of the TypeStack"""
        head: TypeNode  = self.head
        index: int      = 1  # The top element in the stack is number one
        while head is not None:
            print(f"[{index}] {head.value}")
            head = head.next_node
            index += 1

    def pop(self):
        """Remove the head element from the TypeStack linked list"""
        if self.head is None:
            return None
        popped = self.head.value
        self.head = self.head.next_node
        return popped

    def push(self, token_type: TokenType):
        """Add new TypeNode item as the new head to TypeStack linked list"""
        new_head = TypeNode(token_type)
        new_head.next_node = self.head
        self.head = new_head

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
