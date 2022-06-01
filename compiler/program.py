"""
Functions for compile-time type checking and running the Torth program
"""
import copy
import re
import subprocess
from typing import List, Optional
from compiler.defs import Intrinsic, Memory, Op, OpType, Program
from compiler.defs import INTEGER_TYPES, POINTER_TYPES, STACK, Token, TokenType, TypeStack
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
        elif token.type == TokenType.UINT8:
            op_type = OpType.PUSH_UINT8
        elif token_value == 'BOOL':
            op_type = OpType.CAST_BOOL
        elif token_value == 'BREAK':
            op_type = OpType.BREAK
        elif token_value == 'CHAR':
            op_type = OpType.CAST_CHAR
        elif token_value == 'CONTINUE':
            op_type = OpType.CONTINUE
        elif token_value == 'DO':
            op_type = OpType.DO
        elif token_value == 'DONE':
            op_type = OpType.DONE
        elif token_value == 'ELIF':
            op_type = OpType.ELIF
        elif token_value == 'ELSE':
            op_type = OpType.ELSE
        elif token_value == 'END':
            op_type = OpType.END
        elif token_value == 'ENDIF':
            op_type = OpType.ENDIF
        elif token_value == 'IF':
            op_type = OpType.IF
        elif token_value == 'INT':
            op_type = OpType.CAST_INT
        elif token_value == 'PTR':
            op_type = OpType.CAST_PTR
        elif token_value == 'STR':
            op_type = OpType.CAST_STR
        elif token_value == 'UINT8':
            op_type = OpType.CAST_UINT8
        elif token_value == 'WHILE':
            op_type = OpType.WHILE
        elif intrinsic_exists(token_value):
            op_type = OpType.INTRINSIC
        elif function_name_exists(token_value, memories):
            op_type = OpType.PUSH_PTR
        else:
            compiler_error("OP_NOT_FOUND", f"Operation '{token_value}' is not found", token)

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

    branched_stacks: List[TypeStack] = [TypeStack()]
    NOT_TYPED_TOKENS: List[str]      = [ 'BREAK', 'CONTINUE', 'WHILE' ]

    # Save the stack after previous IF / ELIF statements in the IF block to make it possible
    # to type check if-elif chains with different stack layouts than what it was before the block.
    # This is important when there is ELSE present because then we know that the ELSE block will be
    # executed if the previous IF / ELIF conditions were not matched.
    if_block_return_stack: TypeStack    = TypeStack()
    if_block_original_stack: TypeStack  = TypeStack()

    # Track if there was an ELSE clause in the IF block.
    # Required for type checking IF blocks with each IF / ELIF keyword altering the stack state.
    else_present: bool = False

    for op in program:
        token: Token = op.token
        type_stack = branched_stacks[-1]

        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        if op.type == OpType.CAST_BOOL:
            branched_stacks[-1] = type_check_cast_bool(token, type_stack)
        elif op.type == OpType.CAST_CHAR:
            branched_stacks[-1] = type_check_cast_char(token, type_stack)
        elif op.type == OpType.CAST_INT:
            branched_stacks[-1] = type_check_cast_int(token, type_stack)
        elif op.type == OpType.CAST_PTR:
            branched_stacks[-1] = type_check_cast_ptr(token, type_stack)
        elif op.type == OpType.CAST_STR:
            branched_stacks[-1] = type_check_cast_str(token, type_stack)
        elif op.type == OpType.DO:
            branched_stacks[-1] = type_check_do(token, type_stack)
            type_stack = copy.deepcopy(type_stack)
            branched_stacks.append(type_stack)
        elif op.type == OpType.DONE:
            branched_stacks = type_check_end_of_branch(token, branched_stacks)
        elif op.type == OpType.ELIF:
            # Save the state of the stack after the first part of the IF block
            if not if_block_return_stack.head:
                if_block_return_stack = copy.deepcopy(type_stack)

            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                return_stack=if_block_return_stack.get_types())
        elif op.type == OpType.ELSE:
            else_present = True
            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                return_stack=if_block_return_stack.get_types())

            # Use IF block's original stack as the old stack
            branched_stacks.append(if_block_original_stack)
        elif op.type == OpType.ENDIF:
            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                return_stack=if_block_return_stack.get_types())

            # If IF block altered the stack state there MUST be an ELSE to catch all errors
            # and the IF block's return stack must match with the curr
            if not else_present and if_block_return_stack.head and \
                branched_stacks[-1].get_types() != if_block_return_stack.get_types():
                compiler_error("SYNTAX_ERROR", \
                    "The stack state should be the same than at the start of the IF-block.\n" + \
                    "Introduce an ELSE-block if you need to return different values from IF-blocks.\n" + \
                    "The stack state should be the same with every branch of the block.", token)

            # Make the IF block's return stack the new stack for the program
            if if_block_return_stack.head:
                branched_stacks[-1] = if_block_return_stack

            # Reset IF-block variables
            if_block_return_stack = TypeStack()
            else_present = False
        elif op.type == OpType.IF:
            if_block_original_stack = copy.deepcopy(type_stack)
        elif op.type == OpType.PUSH_BOOL:
            branched_stacks[-1] = type_check_push_bool(type_stack)
        elif op.type == OpType.PUSH_CHAR:
            branched_stacks[-1] = type_check_push_char(type_stack)
        elif op.type == OpType.PUSH_INT:
            branched_stacks[-1] = type_check_push_int(type_stack)
        elif op.type == OpType.PUSH_PTR:
            branched_stacks[-1] = type_check_push_ptr(type_stack)
        elif op.type == OpType.PUSH_STR:
            branched_stacks[-1] = type_check_push_str(type_stack)
        elif op.type == OpType.PUSH_UINT8:
            branched_stacks[-1] = type_check_push_uint8(type_stack)
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if intrinsic == "ARGC":
                branched_stacks[-1] = type_check_push_int(type_stack)
            elif intrinsic == "ARGV":
                branched_stacks[-1] = type_check_push_ptr(type_stack)
            elif intrinsic == "DIVMOD":
                branched_stacks[-1] = type_check_divmod(token, type_stack)
            elif intrinsic == "DROP":
                branched_stacks[-1] = type_check_drop(token, type_stack)
            elif intrinsic == "DUP":
                branched_stacks[-1] = type_check_dup(token, type_stack)
            elif intrinsic == "ENVP":
                branched_stacks[-1] = type_check_push_ptr(type_stack)
            elif intrinsic in {"EQ", "GE", "GT", "LE", "LT", "NE"}:
                branched_stacks[-1] = type_check_comparison(token, type_stack)
            elif intrinsic == "INPUT":
                branched_stacks[-1] = type_check_push_str(type_stack)
            elif intrinsic == "LOAD_BOOL":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.BOOL)
            elif intrinsic == "LOAD_CHAR":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.CHAR)
            elif intrinsic == "LOAD_INT":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.INT)
            elif intrinsic == "LOAD_PTR":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.PTR)
            elif intrinsic == "LOAD_STR":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.STR)
            elif intrinsic == "LOAD_UINT8":
                branched_stacks[-1] = type_check_load(token, type_stack, TokenType.UINT8)
            elif intrinsic == "MINUS":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "MUL":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "NTH":
                branched_stacks[-1] = type_check_nth(token, type_stack)
            elif intrinsic == "OVER":
                branched_stacks[-1] = type_check_over(token, type_stack)
            elif intrinsic == "PLUS":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "PRINT":
                branched_stacks[-1] = type_check_print(token, type_stack)
            elif intrinsic == "PUTS":
                branched_stacks[-1] = type_check_puts(token, type_stack)
            elif intrinsic == "ROT":
                branched_stacks[-1] = type_check_rot(token, type_stack)
            elif intrinsic == "STORE_BOOL":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.BOOL)
            elif intrinsic == "STORE_CHAR":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.CHAR)
            elif intrinsic == "STORE_INT":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.INT)
            elif intrinsic == "STORE_PTR":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.PTR)
            elif intrinsic == "STORE_STR":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.STR)
            elif intrinsic == "STORE_UINT8":
                branched_stacks[-1] = type_check_store(token, type_stack, TokenType.UINT8)
            elif intrinsic == "SWAP":
                branched_stacks[-1] = type_check_swap(token, type_stack)
            elif intrinsic == "SWAP2":
                branched_stacks[-1] = type_check_swap2(token, type_stack)
            elif re.fullmatch(r'SYSCALL[0-6]', intrinsic):
                branched_stacks[-1] = type_check_syscall(token, type_stack, int(intrinsic[-1]))
            else:
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

    # The stack should be empty when the program ends.
    # Output the remaining elements in the stack.
    if type_stack.head is not None:
        compiler_error("UNHANDLED_DATA_IN_STACK", \
            "The stack should empty after the program has been executed.\n\n" + \
            f"Unhandled Token types:\n{type_stack.repr()}", token)

def matching_stacks(stack1: List[TokenType], stack2: List[TokenType]) -> bool:
    """Check if two virtual stacks have matching types in them."""
    return not any(type1 != type2 and TokenType.ANY not in {type1, type2} \
        for type1, type2 in zip(stack1, stack2))

def type_check_end_of_branch(token: Token, branched_stacks: List[TypeStack], \
    return_stack: Optional[List[TokenType]] = None) -> List[TypeStack]:
    """
    Check if the stack state is the same after the branch block whether or not the branch condition is matched
    Branch blocks (IF, WHILE) begin with DO and end with DONE, ELIF, ELSE or ENDIF
    """
    stack_after_branch = branched_stacks.pop()
    before_stack: List[TokenType] = branched_stacks[-1].get_types()
    after_stack:  List[TokenType] = stack_after_branch.get_types()

    # Initialize error message
    error: str   = "Stack state should be the same after the block whether or not the condition was matched.\n\n"
    error       += f"Stack state at the start of the block:\n{branched_stacks[-1].repr()}\n"
    error       += f"Stack state at the end of the block:\n{stack_after_branch.repr()}"

    if return_stack:
        if not matching_stacks(return_stack, after_stack):
            compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)
        return branched_stacks

    # Check for different amount of elements in the stack
    if len(before_stack) != len(after_stack):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)

    if not matching_stacks(before_stack, after_stack):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)

    return branched_stacks

def type_check_cast_bool(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    CAST_BOOL explicitely casts the top element of the stack to BOOL type.
    The top element must be an integer to be cast to BOOL.
    """
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", \
            f"Only integer types can be cast to BOOL. Got: {t}\nInteger types: {INTEGER_TYPES}", token)
    type_stack.push(TokenType.BOOL)
    return type_stack

def type_check_cast_char(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    CAST_CHAR explicitely casts the top element of the stack to CHAR type.
    The top element must be INT, PTR or STR to be cast to CHAR.
    """
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", f"Only integer types can be cast to CHAR. Got: {t}", token)
    type_stack.push(TokenType.CHAR)
    return type_stack

def type_check_cast_int(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_INT explicitely casts the top element of the stack to INT type."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_cast_ptr(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_PTR explicitely casts the top element of the stack to PTR type."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    type_stack.push(TokenType.PTR)
    return type_stack

def type_check_cast_str(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_STR explicitely casts the top element of the stack to STR type."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    type_stack.push(TokenType.STR)
    return type_stack

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

def type_check_push_uint8(type_stack: TypeStack) -> TypeStack:
    """Push an unsigned 8-bit integer to the stack"""
    type_stack.push(TokenType.UINT8)
    return type_stack

def type_check_calculations(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    Type check calculation intrinsics like PLUS or MINUS.
    Pop two integers from the stack and push the calculation of the two values.
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 not in INTEGER_TYPES \
    or t2 not in INTEGER_TYPES:
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
    if t1 not in INTEGER_TYPES \
    or t2 not in INTEGER_TYPES:
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

# TODO: Push the correct type from the stack instead of TokenType.ANY
def type_check_nth(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    NTH pops one integer from the stack and pushes the Nth element from stack back to stack.
    Note that the Nth is counted without the popped integer.
    Example: 30 20 10 3 NTH print  // Output: 30 (because 30 is 3rd element without the popped 3).
    """
    t = type_stack.pop()
    if t not in INTEGER_TYPES:
        error_message = f"{token.value.upper()} intrinsic requires an integer. Got: {t}"
        compiler_error("TYPE_ERROR", error_message, token)
    # The type of the value in stack is not always known if the value is from arbitrary memory location
    type_stack.push(TokenType.ANY)
    return type_stack

def type_check_input() -> None:
    """INPUT reads from stdin to buffer and pushes the pointer to the buffer."""
    STACK.append("*buf s_buffer")

def type_check_load(token: Token, type_stack: TypeStack, loaded_type: TokenType) -> TypeStack:
    """
    LOAD variants load certain type of value from where a pointer is pointing to.
    It takes one pointer from the stack and pushes back the dereferenced pointer value.
    Different LOAD variants: LOAD_BOOL, LOAD_CHAR, LOAD_INT, LOAD_PTR, LOAD_STR, LOAD_UINT8.
    """
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty, PTR required.", token)
    if t not in POINTER_TYPES:
        compiler_error("TYPE_ERROR", f"{token.value.upper()} requires a pointer. Got: {t}", token)
    type_stack.push(loaded_type)
    return type_stack

def type_check_over(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    OVER Intrinsic pushes a copy of the element one behind the top element of the stack.
    Example with the stack's top element being the rightmost: a b -> a b a
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "OVER intrinsic requires two values in the stack.", token)
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
    if t not in INTEGER_TYPES:
        compiler_error("TYPE_ERROR", error_message, token)
    return type_stack

def type_check_puts(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop a pointer to string from the stack and print the null-terminated buffer to stdout."""
    t = type_stack.pop()
    error_message = f"PUTS intrinsic requires a pointer to a string buffer. Got: {t}"
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", error_message, token)
    if t not in POINTER_TYPES:
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
    if t1 is None or t2 is None or t3 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "ROT intrinsic requires three values in the stack.", token)
    type_stack.push(t2)
    type_stack.push(t1)
    type_stack.push(t3)
    return type_stack

def type_check_store(token: Token, type_stack: TypeStack, stored_type: TokenType) -> TypeStack:
    """
    STORE variants store a value of certain type to where a pointer is pointing to.
    It takes a pointer and a value from the stack and loads the value to the pointer address.
    Different STORE variants: STORE_BOOL, STORE_CHAR, STORE_INT, STORE_PTR, STORE_STR, STORE_UINT8
    """
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} requires two values on the stack, PTR and value.", token)
    if t1 not in POINTER_TYPES \
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
    if t1 is None or t2 is None:
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
    if t1 is None or t2 is None or t3 is None or t4 is None:
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
