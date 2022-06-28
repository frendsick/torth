"""
Definitions for classes, constants, and types used by the Torth compiler
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union

INCLUDE_PATHS: List[str] = ['.', 'lib']

COLORS: Dict[str, str] = {
    'FAIL'      : '\033[91m',
    'HEADER'    : '\033[95m',
    'NC'        : '\033[0m',
    'WARNING'   : '\033[93m'
}

class Keyword(Enum):
    """Available keywords in the Torth language"""
    BOOL=auto()
    BREAK=auto()
    CHAR=auto()
    CONST=auto()
    CONTINUE=auto()
    DO=auto()
    DONE=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    ENDIF=auto()
    FUNCTION=auto()
    IF=auto()
    INT=auto()
    MEMORY=auto()
    PTR=auto()
    STR=auto()
    UINT8=auto()
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
    LE=auto()
    LOAD_BOOL=auto()
    LOAD_CHAR=auto()
    LOAD_INT=auto()
    LOAD_PTR=auto()
    LOAD_STR=auto()
    LOAD_UINT8=auto()
    LT=auto()
    MINUS=auto()
    MUL=auto()
    NE=auto()
    NTH=auto()
    OR=auto()
    OVER=auto()
    PLUS=auto()
    PRINT=auto()
    ROT=auto()
    STORE_BOOL=auto()
    STORE_CHAR=auto()
    STORE_INT=auto()
    STORE_PTR=auto()
    STORE_STR=auto()
    STORE_UINT8=auto()
    SWAP=auto()
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
    CAST_BOOL=auto()
    CAST_CHAR=auto()
    CAST_INT=auto()
    CAST_PTR=auto()
    CAST_STR=auto()
    CAST_UINT8=auto()
    CONTINUE=auto()
    DO=auto()
    DONE=auto()
    ELIF=auto()
    ELSE=auto()
    END=auto()
    ENDIF=auto()
    FUNCTION_CALL=auto()
    FUNCTION_RETURN=auto()
    IF=auto()
    INTRINSIC=auto()
    PUSH_BOOL=auto()
    PUSH_CHAR=auto()
    PUSH_INT=auto()
    PUSH_PTR=auto()
    PUSH_STR=auto()
    PUSH_UINT8=auto()
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
    UINT8=auto()
    WORD=auto()

INTEGER_TYPES: List[TokenType] = [
    TokenType.ANY,
    TokenType.BOOL,
    TokenType.CHAR,
    TokenType.INT,
    TokenType.UINT8
]

POINTER_TYPES: List[TokenType] = [
    TokenType.ANY,
    TokenType.PTR,
    TokenType.STR
]

@dataclass
class TypeNode:
    """Node for TypeStack linked list containing the current Token's type"""
    value: TokenType
    location: Location
    next_node: Union[TypeNode, None] = None

class TypeStack:
    """Linked list containing the types on the virtual stack used in type checking"""
    def __init__(self) -> None:
        self.head: Union[TypeNode, None] = None

    def repr(self) -> str:
        """Return the types in the TypeStack in printable fashion"""
        head: Optional[TypeNode] = self.head
        index: int      = 1  # The top element in the stack is number one
        contents: str   = ''
        while head is not None:
            contents += f"[{index}] {head.value} {head.location}\n"
            head = head.next_node
            index += 1
        return contents

    def print(self) -> None:
        """Print the contents of the TypeStack"""
        print(self.repr())

    def pop(self) -> Optional[TypeNode]:
        """Remove the head element from the TypeStack linked list"""
        if self.head is None:
            return None
        popped: TypeNode = self.head
        self.head = self.head.next_node
        return popped

    def push(self, token_type: TokenType, location: Location) -> None:
        """Add new TypeNode item as the new head to TypeStack linked list"""
        new_head = TypeNode(token_type, location)
        new_head.next_node = self.head
        self.head = new_head

    def get_types(self) -> List[TokenType]:
        """Returns list of TokenTypes in the TypeStack"""
        head: Optional[TypeNode] = self.head
        node_list: List[TokenType] = []
        while head is not None:
            node_list.append(head.value)
            head = head.next_node
        return node_list

Location = Tuple[str, int, int]      # Source file name, row, column

@dataclass
class Constant:
    """CONST keyword can be used to create a named immutable integer value"""
    name: str
    value: int
    location: Location

@dataclass
class Memory:
    """MEMORY is a named memory location with a size"""
    name: str
    size: int
    location: Location

@dataclass
class Token:
    """Tokens are words from a program that translates to certain operands"""
    value: str
    type: TokenType
    location: Location

# param types, return types
Signature = Tuple[List[TokenType], List[TokenType]]
SIGNATURE_MAP: Dict[str, TokenType] = {
    'ANY':      TokenType.ANY,
    'BOOL':     TokenType.BOOL,
    'CHAR':     TokenType.CHAR,
    'INT':      TokenType.INT,
    'PTR':      TokenType.PTR,
    'STR':      TokenType.PTR,
    'UINT8':    TokenType.UINT8
}

@dataclass
class Function:
    """Functions are reusable named sequences of Token objects"""
    name: str
    signature: Signature
    tokens: List[Token]

@dataclass
class Op:
    """Operands are commands in the intermediate representetion used in assembly code generation"""
    id: int
    type: OpType
    token: Token
    func: Function

Program = List[Op]
