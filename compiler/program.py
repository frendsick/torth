"""
Functions for compile-time type checking and running the Torth program
"""
import re
import subprocess
from typing import List
from compiler.defs import Intrinsic, Memory, Op, OpType, Program
from compiler.defs import STACK, Token, TokenType, TypeStack
from compiler.utils import compiler_error

def generate_program(tokens: List[Token], memories: List[Memory]) -> Program:
    """Generate a Program from a list of Tokens. Return the Program."""
    program: List[Op] = []
    for op_id, token in enumerate(tokens):
        token_value: str = token.value.upper()
        if token.type == TokenType.BOOL:
            op_type = OpType.PUSH_BOOL
        elif token.type == TokenType.CHAR:
            op_type = OpType.PUSH_CHAR
        elif token.type == TokenType.INT:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.STR:
            op_type = OpType.PUSH_STR
        elif token_value == 'BREAK':
            op_type = OpType.BREAK
        elif token_value == 'DO':
            op_type = OpType.DO
        elif token_value == 'DONE':
            op_type = OpType.DONE
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
        elif function_name_exists(token_value, memories):
            op_type = OpType.PUSH_PTR
        else:
            compiler_error("OP_NOT_FOUND", f"Operation '{token_value}' is not found")

        program.append( Op(op_id, op_type, token) )
    return program

def intrinsic_exists(token_value: str) -> bool:
    """Return boolean value whether or not certain Intrinsic exists."""
    return bool(hasattr(Intrinsic, token_value))

def function_name_exists(token: str, memories: List[Memory]) -> bool:
    """Return boolean value whether or not certain Function exists."""
    for memory in memories:
        memory_name = memory[0]
        if memory_name.upper() == token:
            return True
    return False

def run_code(exe_file: str) -> None:
    """Run an executable"""
    subprocess.run([f'./{exe_file}'], check=True)

def type_check_program(program: Program) -> None:
    """
    Type check all Operands of the Program.
    Raise compiler error if the type checking fails.
    """

    type_stack = TypeStack()
    NOT_TYPED_TOKENS: List[str] = [ 'BREAK', 'DONE', 'ELIF', 'ELSE', 'ENDIF', 'IF', 'WHILE' ]
    for op in program:
        token: Token = op.token
        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        if op.type == OpType.DO:
            type_stack = type_check_do(token, type_stack)
        elif op.type == OpType.PUSH_BOOL:
            type_stack = type_check_push_bool(type_stack)
        elif op.type == OpType.PUSH_CHAR:
            type_stack = type_check_push_char(type_stack)
        elif op.type == OpType.PUSH_INT:
            type_stack = type_check_push_int(type_stack)
        elif op.type == OpType.PUSH_PTR:
            type_stack = type_check_push_ptr(type_stack)
        elif op.type == OpType.PUSH_STR:
            type_stack = type_check_push_str(type_stack)
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if intrinsic == "DIVMOD":
                type_stack = type_check_divmod(token, type_stack)
            elif intrinsic == "DROP":
                type_stack = type_check_drop(token, type_stack)
            elif intrinsic == "DUP":
                type_stack = type_check_dup(token, type_stack)
            elif intrinsic == "ENVP":
                type_stack = type_check_push_ptr(type_stack)
            elif intrinsic in {"EQ", "GE", "GT", "LE", "LT", "NE"}:
                type_stack = type_check_comparison(token, type_stack)
            elif intrinsic == "HERE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "INPUT":
                type_stack = type_check_push_str(type_stack)
            elif intrinsic == "LOAD_BOOL":
                type_stack = type_check_load(token, type_stack, TokenType.BOOL)
            elif intrinsic == "LOAD_CHAR":
                type_stack = type_check_load(token, type_stack, TokenType.CHAR)
            elif intrinsic == "LOAD_INT":
                type_stack = type_check_load(token, type_stack, TokenType.INT)
            elif intrinsic == "LOAD_PTR":
                type_stack = type_check_load(token, type_stack, TokenType.PTR)
            elif intrinsic == "LOAD_STR":
                type_stack = type_check_load(token, type_stack, TokenType.STR)
            elif intrinsic == "MINUS":
                type_stack = type_check_calculations(token, type_stack)
            elif intrinsic == "MUL":
                type_stack = type_check_calculations(token, type_stack)
            elif intrinsic == "NTH":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "OVER":
                type_stack = type_check_over(token, type_stack)
            elif intrinsic == "PLUS":
                type_stack = type_check_calculations(token, type_stack)
            elif intrinsic == "PRINT":
                type_stack = type_check_print(token, type_stack)
            elif intrinsic == "PUTS":
                type_stack = type_check_puts(token, type_stack)
            elif intrinsic == "ROT":
                type_stack = type_check_rot(token, type_stack)
            elif intrinsic == "STORE_BOOL":
                type_stack = type_check_store(token, type_stack, TokenType.BOOL)
            elif intrinsic == "STORE_CHAR":
                type_stack = type_check_store(token, type_stack, TokenType.CHAR)
            elif intrinsic == "STORE_INT":
                type_stack = type_check_store(token, type_stack, TokenType.INT)
            elif intrinsic == "STORE_PTR":
                type_stack = type_check_store(token, type_stack, TokenType.PTR)
            elif intrinsic == "STORE_STR":
                type_stack = type_check_store(token, type_stack, TokenType.STR)
            elif intrinsic == "SWAP":
                type_stack = type_check_swap(token, type_stack)
            elif intrinsic == "SWAP2":
                type_stack = type_check_swap2(token, type_stack)
            elif re.fullmatch(r'SYSCALL[0-6]', intrinsic):
                type_stack = type_check_syscall(token, type_stack, int(intrinsic[-1]))
            else:
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

def type_check_do(token: Token, type_stack: TypeStack) -> TypeStack:
    """DO Keyword pops two items from the stack"""
    _  = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "DO requires two values to the stack.", token)
    return type_stack

def type_check_push_bool(type_stack: TypeStack) -> TypeStack:
    """Push a boolean to the stack"""
    type_stack.push(TokenType.BOOL)
    return type_stack

def type_check_push_char(type_stack: TypeStack) -> TypeStack:
    """Push a character to the stack"""
    type_stack.push(TokenType.CHAR)
    return type_stack

def type_check_push_int(type_stack: TypeStack) -> TypeStack:
    """Push an integer to the stack"""
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_push_ptr(type_stack: TypeStack) -> TypeStack:
    """Push a pointer to the stack"""
    type_stack.push(TokenType.PTR)
    return type_stack

def type_check_push_str(type_stack: TypeStack) -> TypeStack:
    """Push a string to the stack"""
    type_stack.push(TokenType.STR)
    return type_stack

def type_check_calculations(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    Type check calculation intrinsics like PLUS or MINUS.
    Pop two integers from the stack and push the calculation of the two values.
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 not in {TokenType.ANY, TokenType.INT} \
    or t2 not in {TokenType.ANY, TokenType.INT}:
        error_message = f"{token.value.upper()} intrinsic requires two integers. Got: {t1}, {t2}"
        compiler_error("TYPE_ERROR", error_message, token)
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_comparison(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    Type check calculation comparison intrinsics like EQ or GE.
    Comparison intrinsics take two elements from the stack and compares them.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    _  = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "EQ requires two values to the stack.", token)
    type_stack.push(t2)
    type_stack.push(TokenType.BOOL)
    return type_stack

def type_check_divmod(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    DIVMOD pops two items from the stack and divides second from the top one.
    Pop two integers from the stack and push the remainder and the quotient of the two values.
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 not in {TokenType.ANY, TokenType.INT} \
    or t2 not in {TokenType.ANY, TokenType.INT}:
        error_message = f"{token.value.upper()} intrinsic requires two integers. Got: {t1}, {t2}"
        compiler_error("TYPE_ERROR", error_message, token)
    type_stack.push(TokenType.INT)
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_drop(token: Token, type_stack: TypeStack) -> TypeStack:
    """DROP removes one item from the stack."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.", token)
    return type_stack

def type_check_dup(token: Token, type_stack: TypeStack) -> TypeStack:
    """DUP duplicates the top item from the stack."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.", token)
    type_stack.push(t)
    type_stack.push(t)
    return type_stack

def type_check_nth(token: Token) -> None:
    """
    NTH pops one integer from the stack and pushes the Nth element from stack back to stack.
    Note that the Nth is counted without the popped integer.
    Example: 30 20 10 3 NTH print  // Output: 30 (because 30 is 3rd element without the popped 3).
    """
    # The top element in the stack is the N
    try:
        n: int = int(STACK.pop()) - 1
        if n < 0:
            raise ValueError
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)
    except ValueError:
        compiler_error("STACK_VALUE_ERROR", "First element in the stack is not a non-zero positive integer.", token)
    try:
        stack_index: int = len(STACK) - 1
        nth_element: str = STACK[stack_index - n]
    except IndexError:
        compiler_error("NOT_ENOUGH_ELEMENTS_IN_STACK", \
                    f"Cannot get {n+1}. element from the stack: Stack only contains {len(STACK)} elements.", token)
    STACK.append(nth_element)

def type_check_input() -> None:
    """INPUT reads from stdin to buffer and pushes the pointer to the buffer."""
    STACK.append("*buf s_buffer")

def type_check_load(token: Token, type_stack: TypeStack, loaded_type: TokenType) -> TypeStack:
    """
    LOAD variants load certain type of value from where a pointer is pointing to.
    It takes one pointer from the stack and pushes back the dereferenced pointer value.
    Different LOAD variants: LOAD_BYTE, LOAD_QWORD.
    """
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty, PTR required.", token)
    if t != TokenType.PTR:
        compiler_error("TYPE_ERROR", f"{token.value.upper()} requires PTR to the top of the stack Got: {t}")
    type_stack.push(loaded_type)
    return type_stack

def type_check_over(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    OVER Intrinsic pushes a copy of the element one behind the top element of the stack.
    Example with the stack's top element being the rightmost: a b -> a b a
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "OVER intrinsic requires four values in the stack.", token)
    type_stack.push(t2)
    type_stack.push(t1)
    type_stack.push(t2)
    return type_stack

def type_check_print(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop an integer from the stack and print the value of it to the stdout."""
    t = type_stack.pop()
    error_message = f"PRINT intrinsic requires an integer. Got: {t}"
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", error_message, token)
    if t != TokenType.INT:
        compiler_error("TYPE_ERROR", error_message, token)
    return type_stack

def type_check_puts(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop a pointer to string from the stack and print the null-terminated buffer to stdout."""
    t = type_stack.pop()
    error_message = f"PUTS intrinsic requires a string. Got: {t}"
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", error_message, token)
    if t != TokenType.STR:
        compiler_error("TYPE_ERROR", error_message, token)
    return type_stack

def type_check_rot(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    ROT Intrinsic rotates the top three elements of the stack so that the third becomes first.
    Example with the stack's top element being the rightmost: a b c -> b c a
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    t3 = type_stack.pop()
    if t3 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "ROT intrinsic requires four values in the stack.", token)
    type_stack.push(t2)
    type_stack.push(t1)
    type_stack.push(t3)
    return type_stack

def type_check_store(token: Token, type_stack: TypeStack, stored_type: TokenType) -> TypeStack:
    """
    STORE variants store a value of certain type to where a pointer is pointing to.
    It takes a pointer and a value from the stack and loads the value to the pointer address.
    Different STORE variants: STORE_BOOL, STORE_CHAR, STORE_INT, STORE_PTR, STORE_STR
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} requires two values on the stack, PTR and value.", token)
    if t1 not in {TokenType.ANY, TokenType.PTR} \
    or t2 not in {TokenType.ANY, stored_type}:
        compiler_error("TYPE_ERROR", f"Expected: {TokenType.PTR}, {stored_type}.\nGot: {t1}, {t2}", token)
    return type_stack

def type_check_swap(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    SWAP Intrinsic swaps two top elements in the stack.
    Example with the stack's top element being the rightmost: a b -> b a
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "SWAP intrinsic requires two values in the stack.", token)
    type_stack.push(t1)
    type_stack.push(t2)
    return type_stack

def type_check_swap2(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    SWAP2 Intrinsic swaps the two pairs of two top elements in the stack.
    Example with the stack's top element being the rightmost: a b c d -> c d a b
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    t3 = type_stack.pop()
    t4 = type_stack.pop()
    if t4 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "SWAP2 intrinsic requires four values in the stack.", token)
    type_stack.push(t2)
    type_stack.push(t1)
    type_stack.push(t4)
    type_stack.push(t3)
    return type_stack

def type_check_syscall(token: Token, type_stack: TypeStack, param_count: int) -> TypeStack:
    """
    SYSCALL intrinsic variants call a Linux syscall.
    Syscalls require different amount of arguments from 0 to 6.
    Different variants are named SYSCALL0 - SYSCALL6 by the amount of arguments.
    The different syscall constants required for RAX register can be found from lib/sys.torth.
    Naming convention (case sensitive): SYS_<syscall> - Example: SYS_write

    https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#tables
    """
    for _ in range(param_count+1):
        t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} intrinsic requires {param_count+1} values in the stack.", token)
    type_stack.push(TokenType.INT)  # Syscall return code
    return type_stack
