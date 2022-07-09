"""
Functions for compile-time type checking and running the Torth program
"""
import re
from copy import copy
from typing import Dict, List, Optional
from compiler.defs import Function, Intrinsic, Location, Memory, Op, OpType
from compiler.defs import Program, Signature, Token, TokenType, TypeStack
from compiler.defs import INTEGER_TYPES, POINTER_TYPES
from compiler.utils import compiler_error, equal_type_lists

def generate_program(tokens: List[Token], functions: List[Function], memories: List[Memory]) -> Program:
    """Generate a Program from a list of Tokens. Return the Program."""
    program: List[Op] = []
    tokens_function_cache: Dict[Location, Function] = {}
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
        elif token_value.endswith('_CALL'):
            op_type = OpType.FUNCTION_CALL
        elif token_value.endswith('_RETURN'):
            op_type = OpType.FUNCTION_RETURN
        elif intrinsic_exists(token_value):
            op_type = OpType.INTRINSIC
        elif memory_exists(token_value, memories):
            op_type = OpType.PUSH_PTR
        else:
            compiler_error("OP_NOT_FOUND", f"Operation '{token_value}' is not found", token)

        if token.location not in tokens_function_cache:
            tokens_function_cache[token.location] = get_tokens_function(token, functions)
        func: Function = tokens_function_cache[token.location]
        program.append( Op(op_id, op_type, token, func) )
    return program

def get_tokens_function(token: Token, functions: List[Function]) -> Function:
    """Determine the corresponding function for a Token"""
    for func in functions:
        for func_token in func.tokens:
            if token.location == func_token.location:
                return func
    compiler_error("COMPILER_ERROR", \
        f"Could not determine corresponding Function for Token '{token.value}'", token)

def intrinsic_exists(token_value: str) -> bool:
    """Return boolean value whether or not certain Intrinsic exists."""
    return bool(hasattr(Intrinsic, token_value))

def memory_exists(token: str, memories: List[Memory]) -> bool:
    """Return boolean value whether or not certain Memory exists."""
    return any(memory.name.upper() == token for memory in memories)

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
    if_block_return_stack: TypeStack = TypeStack()

    # Save the stack at the beginning of the IF block to enable altering the stack state during IF block.
    # This is a list of stacks to enable nested IF blocks.
    if_block_original_stacks: List[TypeStack] = [TypeStack()]

    # Track if there was an ELSE clause in the IF block.
    # Required for type checking IF blocks with each IF / ELIF keyword altering the stack state.
    else_present: bool = False

    # Store the amount of items in the stack before each function call
    original_function_stacks: List[TypeStack] = [TypeStack()]

    for op in program:
        token: Token = op.token
        type_stack: TypeStack = branched_stacks[-1]

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
        elif op.type == OpType.CAST_UINT8:
            branched_stacks[-1] = type_check_cast_uint8(token, type_stack)
        elif op.type == OpType.DO:
            branched_stacks[-1] = type_check_do(token, type_stack, branched_stacks)
        elif op.type == OpType.DONE:
            branched_stacks = type_check_end_of_branch(token, branched_stacks)
        elif op.type == OpType.ELIF:
            # Save the state of the stack after the first part of the IF block
            if not if_block_return_stack.head:
                if_block_return_stack = copy(type_stack)

            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                if_block_return_stack=if_block_return_stack)
        elif op.type == OpType.ELSE:
            else_present = True

            # Save the state of the stack after the first part of the IF block
            if not if_block_return_stack.head:
                if_block_return_stack = copy(type_stack)

            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                if_block_return_stack=if_block_return_stack)

            # Use IF block's original stack as the old stack
            branched_stacks.append(if_block_original_stacks[-1])
        elif op.type == OpType.ENDIF:
            # Save the state of the stack after the first part of the IF block
            if not if_block_return_stack.head:
                if_block_return_stack = copy(type_stack)
            branched_stacks = type_check_end_of_branch(token, branched_stacks, \
                if_block_return_stack=if_block_return_stack)

            # If IF block altered the stack state there MUST be an ELSE to catch all errors
            # and the IF block's return stack must match with all of the sections in the block
            if not else_present and if_block_return_stack.head and \
                not equal_type_lists(branched_stacks[-1].get_types(), if_block_return_stack.get_types()):
                compiler_error("SYNTAX_ERROR", \
                    "The stack state should be the same than at the start of the IF-block.\n" + \
                    "Introduce an ELSE-block if you need to return different values from IF-blocks.\n" + \
                    "The stack state should be the same with every branch of the block.\n\n" + \
                    f"Stack state after the previous sections in the IF block:\n{if_block_return_stack.repr()}\n" + \
                    f"The stack state before the IF block:\n{branched_stacks[-1].repr()}")

            # Make the IF block's return stack the new stack for the program
            if if_block_return_stack.head:
                branched_stacks[-1] = if_block_return_stack

            # Reset IF-block variables
            if_block_original_stacks.pop()
            if_block_return_stack = TypeStack()
            else_present = False
        elif op.type == OpType.FUNCTION_CALL:
            type_check_function_call(op, type_stack, original_function_stacks)
        elif op.type == OpType.FUNCTION_RETURN:
            type_check_function_return(op, op.func.signature, type_stack, original_function_stacks.pop())
        elif op.type == OpType.IF:
            if_block_original_stacks.append(copy(type_stack))
        elif op.type == OpType.PUSH_BOOL:
            branched_stacks[-1] = type_check_push_bool(token, type_stack)
        elif op.type == OpType.PUSH_CHAR:
            branched_stacks[-1] = type_check_push_char(token, type_stack)
        elif op.type == OpType.PUSH_INT:
            branched_stacks[-1] = type_check_push_int(token, type_stack)
        elif op.type == OpType.PUSH_PTR:
            branched_stacks[-1] = type_check_push_ptr(token, type_stack)
        elif op.type == OpType.PUSH_STR:
            branched_stacks[-1] = type_check_push_str(token, type_stack)
        elif op.type == OpType.PUSH_UINT8:
            branched_stacks[-1] = type_check_push_uint8(token, type_stack)
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if intrinsic == "AND":
                branched_stacks[-1] = type_check_bitwise(token, type_stack)
            elif intrinsic == "ARGC":
                branched_stacks[-1] = type_check_push_int(token, type_stack)
            elif intrinsic == "ARGV":
                branched_stacks[-1] = type_check_push_ptr(token, type_stack)
            elif intrinsic == "DIVMOD":
                branched_stacks[-1] = type_check_divmod(token, type_stack)
            elif intrinsic == "DROP":
                branched_stacks[-1] = type_check_drop(token, type_stack)
            elif intrinsic == "DUP":
                branched_stacks[-1] = type_check_dup(token, type_stack)
            elif intrinsic == "ENVP":
                branched_stacks[-1] = type_check_push_ptr(token, type_stack)
            elif intrinsic in {"EQ", "GE", "GT", "LE", "LT", "NE"}:
                branched_stacks[-1] = type_check_comparison(token, type_stack)
            elif intrinsic.startswith("LOAD_"):
                branched_stacks[-1] = type_check_load(token, type_stack)
            elif intrinsic == "MINUS":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "MUL":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "NTH":
                branched_stacks[-1] = type_check_nth(token, type_stack)
            elif intrinsic == "OR":
                branched_stacks[-1] = type_check_bitwise(token, type_stack)
            elif intrinsic == "OVER":
                branched_stacks[-1] = type_check_over(token, type_stack)
            elif intrinsic == "PLUS":
                branched_stacks[-1] = type_check_calculations(token, type_stack)
            elif intrinsic == "PRINT":
                branched_stacks[-1] = type_check_print(token, type_stack)
            elif intrinsic == "ROT":
                branched_stacks[-1] = type_check_rot(token, type_stack)
            elif intrinsic.startswith("STORE_"):
                branched_stacks[-1] = type_check_store(token, type_stack)
            elif intrinsic == "SWAP":
                branched_stacks[-1] = type_check_swap(token, type_stack)
            elif re.fullmatch(r'SYSCALL[0-6]', intrinsic):
                branched_stacks[-1] = type_check_syscall(token, type_stack, int(intrinsic[-1]))
            else:
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

    # There should be one INT in the stack when the program ends.
    # Output the remaining elements in the stack.
    if type_stack.get_types() != [TokenType.INT]:
        compiler_error("FUNCTION_SIGNATURE_ERROR", \
            "Only the integer return value of the program should be in the stack when program exits.\n\n" + \
            f"Stack after the MAIN function:\n{type_stack.repr()}")

def type_check_function_call(op: Op, type_stack: TypeStack, \
    original_function_stacks: List[TypeStack]) -> List[TokenType]:
    """
    Type check the function parameter types.
    Returns the types in stack when the parameters are popped out.
    """
    param_types: List[TokenType] = op.func.signature[0]
    original_function_stacks.append(copy(type_stack))
    temp_stack = copy(type_stack)
    for param_type in param_types:
        if not temp_stack.head:
            compiler_error("FUNCTION_SIGNATURE_ERROR", \
                f"Function '{op.func.name}' requires more values to the stack.\n\n" + \
                f"Expected parameter types: {param_types}", op.token, current_stack=type_stack)
        top_type: TokenType = temp_stack.pop().value  # type: ignore

        # Check for any type and pointers
        if param_type == TokenType.ANY or top_type == TokenType.ANY or \
            (param_type in POINTER_TYPES and top_type in POINTER_TYPES):
            continue
        # Check all other types
        if param_type not in [top_type, TokenType.ANY]:
            compiler_error("FUNCTION_SIGNATURE_ERROR", \
                f"Function '{op.func.name}' has wrong parameter types in the stack.\n\n" + \
                f"Expected parameter types: {param_types}", op.token, current_stack=type_stack)
    return temp_stack.get_types()

def type_check_function_return(op: Op, function_signature: Signature, \
    type_stack: TypeStack, function_call_stack: TypeStack) -> None:
    """Type check the function return types"""
    return_types: List[TokenType] = function_signature[1]
    temp_stack = copy(type_stack)
    for return_type in return_types:
        if not temp_stack.head:
            compiler_error("FUNCTION_SIGNATURE_ERROR", \
                f"Function '{op.func.name}' requires more values in the stack when the function returns.\n\n" + \
                f"Expected return types: {return_types}", op.token, current_stack=type_stack)

        # Check for any type and pointers
        top_type: TokenType = temp_stack.pop().value  # type: ignore
        if return_type == TokenType.ANY or top_type == TokenType.ANY \
            or (return_type in POINTER_TYPES and top_type in POINTER_TYPES):
            continue
        # Check all other types
        if return_type not in [top_type, TokenType.ANY]:
            compiler_error("FUNCTION_SIGNATURE_ERROR", \
                f"Function '{op.func.name}' has wrong return types in the stack.\n\n" + \
                f"Expected return types: {return_types}", op.token, current_stack=type_stack)

    # Check if the function consumes the correct amount of values from the stack
    stack_difference: int = len(function_signature[0]) - len(return_types)
    if stack_difference != len(function_call_stack.get_types()) - len(type_stack.get_types()):
        expected_types: TypeStack = copy(type_stack)
        for _ in return_types:
            expected_types.pop()
        compiler_error("FUNCTION_SIGNATURE_ERROR", \
            f"Function '{op.func.name}' does not use the values determined in function signature\n\n" + \
            f"Function Signature:\n{function_signature}\n\n" + \
            f"Stack before the function call:\n{function_call_stack.repr()}\n" + \
            f"Stack after the function call:\n{type_stack.repr()}")

def matching_stacks(stack1: List[TokenType], stack2: List[TokenType]) -> bool:
    """Check if two virtual stacks have matching types in them."""
    return not any(type1 != type2 and TokenType.ANY not in {type1, type2} \
        for type1, type2 in zip(stack1, stack2))

def type_check_end_of_branch(token: Token, branched_stacks: List[TypeStack], \
    if_block_return_stack: Optional[TypeStack] = None) -> List[TypeStack]:
    """
    Check if the stack state is the same after the branch block whether or not the branch condition is matched
    Branch blocks (IF, WHILE) begin with DO and end with DONE, ELIF, ELSE or ENDIF
    """
    stack_after_branch = branched_stacks.pop()
    try:
        before_types: List[TokenType] = branched_stacks[-1].get_types()
    except IndexError:
        block_type: str = 'IF' if token.value.upper() == 'ENDIF' else 'WHILE'
        compiler_error("SYNTAX_ERROR", f"{token.value.upper()} token found outside {block_type} block.", token)
    after_types:  List[TokenType] = stack_after_branch.get_types()

    # Check if stack states are different between sections inside IF block
    if if_block_return_stack:
        return_types: List[TokenType] = if_block_return_stack.get_types()
        if not matching_stacks(return_types, after_types):
            error: str   =  "Stack state should be the same after each section in the IF block.\n\n"
            error       += f"Stack state after previous sections:\n{if_block_return_stack.repr()}\n"
            error       += f"Stack state after the current section:\n{stack_after_branch.repr()}"
            compiler_error("DIFFERENT_STACK_BETWEEN_SECTIONS", error, token)
        return branched_stacks

    # Check for different stack states before and after the block
    error  = "Stack state should be the same after the block whether or not the condition was matched.\n\n"
    error += f"Stack state at the start of the block:\n{branched_stacks[-1].repr()}\n"
    error += f"Stack state at the end of the block:\n{stack_after_branch.repr()}"
    if len(before_types) != len(after_types):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)
    if not matching_stacks(before_types, after_types):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)

    return branched_stacks

def type_check_cast_bool(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    CAST_BOOL explicitely casts the top element of the stack to BOOL type.
    The top element must be an integer to be cast to BOOL.
    """
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", \
            f"Only integer types can be cast to BOOL.\nInteger types: {INTEGER_TYPES}\n\n" + \
            f"Popped type:\n{t.value} {t.location}", token, current_stack=temp_stack)
    type_stack.push(TokenType.BOOL, token.location)
    return type_stack

def type_check_cast_char(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    CAST_CHAR explicitely casts the top element of the stack to CHAR type.
    The top element must be INT, PTR or STR to be cast to CHAR.
    """
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value == TokenType.BOOL:
        compiler_error("VALUE_ERROR", "A boolean value cannot be cast to CHAR.", token, current_stack=temp_stack)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", "Only integer-like values can be cast to CHAR.", token, current_stack=temp_stack)
    type_stack.push(TokenType.CHAR, token.location)
    return type_stack

def type_check_cast_int(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_INT explicitely casts the top element of the stack to INT type."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    type_stack.push(TokenType.INT, token.location)
    return type_stack

def type_check_cast_ptr(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_PTR explicitely casts the top element of the stack to PTR type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value in {TokenType.BOOL, TokenType.CHAR}:
        compiler_error("VALUE_ERROR", f"{t.value} cannot be cast to PTR.", token, current_stack=temp_stack)
    type_stack.push(TokenType.PTR, token.location)
    return type_stack

def type_check_cast_str(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_STR explicitely casts the top element of the stack to STR type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value not in POINTER_TYPES:
        compiler_error("VALUE_ERROR", "Only pointer-like values can be cast to STR.", token, current_stack=temp_stack)
    type_stack.push(TokenType.STR, token.location)
    return type_stack

def type_check_cast_uint8(token: Token, type_stack: TypeStack) -> TypeStack:
    """CAST_UINT8 explicitely casts the top element of the stack to UINT8 type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", "Only integer-like values can be cast to UINT8.", token, current_stack=temp_stack)
    type_stack.push(TokenType.UINT8, token.location)
    return type_stack

def type_check_do(token: Token, type_stack: TypeStack, branched_stacks: List[TypeStack]) -> TypeStack:
    """DO Keyword pops one boolean from the stack"""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "DO requires two values to the stack.", token)
    if t.value not in { TokenType.BOOL, TokenType.ANY }:
        compiler_error("VALUE_ERROR", "DO requires a boolean.\n\n" + \
            f"Popped types:\n{t.value} {t.location}", token, current_stack=temp_stack)

    type_stack = copy(type_stack)
    branched_stacks.append(type_stack)
    return type_stack

def type_check_push_bool(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push a boolean to the stack"""
    type_stack.push(TokenType.BOOL, token.location)
    return type_stack

def type_check_push_char(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push a character to the stack"""
    type_stack.push(TokenType.CHAR, token.location)
    return type_stack

def type_check_push_int(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push an integer to the stack"""
    type_stack.push(TokenType.INT, token.location)
    return type_stack

def type_check_push_ptr(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push a pointer to the stack"""
    type_stack.push(TokenType.PTR, token.location)
    return type_stack

def type_check_push_str(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push a string to the stack"""
    type_stack.push(TokenType.STR, token.location)
    return type_stack

def type_check_push_uint8(token: Token, type_stack: TypeStack) -> TypeStack:
    """Push an unsigned 8-bit integer to the stack"""
    type_stack.push(TokenType.UINT8, token.location)
    return type_stack

def type_check_bitwise(token: Token, type_stack: TypeStack) -> TypeStack:
    """AND performs bitwise-AND operation to two integers."""
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", f"{token.value} intrinsic requires two integers.", token)
    if t1.value not in INTEGER_TYPES or t2.value not in INTEGER_TYPES:
        error_message = f"{token.value} intrinsic requires two integers.\n\n" + \
            f"Popped types:\n{t1.value} {t1.location}\n{t2.value} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)
    return type_stack

def type_check_calculations(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    Type check calculation intrinsics like PLUS or MINUS.
    Pop two integers from the stack and push the calculation of the two values.
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", f"{token.value} requires two values to the stack.\n\n" \
            f"Stack contents:\n{type_stack.repr()}", token)
    if t1.value not in INTEGER_TYPES \
    or t2.value not in INTEGER_TYPES:
        error_message = f"{token.value.upper()} intrinsic requires two integers.\n\n" + \
            f"Popped types:\n{t1.value} {t1.location}\n{t2.value} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)

    type_stack.push(TokenType.INT, token.location)
    return type_stack

def type_check_comparison(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    Type check calculation comparison intrinsics like EQ or GE.
    Comparison intrinsics take two elements from the stack and compares them.
    It pushes a boolean value of the comparison.
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", f"{token.value} requires two values to the stack.\n\n" \
            f"Stack contents:\n{type_stack.repr()}", token)
    if t1.value not in INTEGER_TYPES \
    or t2.value not in INTEGER_TYPES:
        error_message = f"{token.value.upper()} intrinsic requires two integers.\n\n" + \
            f"Popped types:\n{t1.value} {t1.location}\n{t2.value} {t2.location}"
        compiler_error("TYPE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.BOOL, token.location)
    return type_stack

def type_check_divmod(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    DIVMOD pops two items from the stack and divides second from the top one.
    Pop two integers from the stack and push the remainder and the quotient of the two values.
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "DIVMOD requires two values to the stack.", token)
    if t1.value not in INTEGER_TYPES \
    or t2.value not in INTEGER_TYPES:
        error_message = f"{token.value.upper()} intrinsic requires two integers.\n\n" + \
            f"Popped types:\n{t1.value} {t1.location}\n{t2.value} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)
    type_stack.push(TokenType.INT, token.location)
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
    type_stack.push(t.value, t.location)
    type_stack.push(t.value, t.location)
    return type_stack

# TODO: Push the correct type from the stack instead of TokenType.ANY
def type_check_nth(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    NTH pops one integer from the stack and pushes the Nth element from stack back to stack.
    Note that the Nth is counted without the popped integer.
    Example: 30 20 10 3 NTH print  // Output: 30 (because 30 is 3rd element without the popped 3).
    """
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "NTH intrinsic requires an integer.", token)
    if t.value not in INTEGER_TYPES:
        error_message = "NTH intrinsic requires an integer.\n\n" + \
            f"Popped type:\n{t.value} {t.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)
    # The type of the value in stack is not always known if the value is from arbitrary memory location
    type_stack.push(TokenType.ANY, token.location)
    return type_stack

def type_check_load(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    LOAD variants load certain type of value from where a pointer is pointing to.
    It takes one pointer from the stack and pushes back the dereferenced pointer value.
    Different LOAD variants: LOAD_BYTE, LOAD_WORD, LOAD_DWORD, LOAD_QWORD
    """
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty, PTR required.", token)
    if t.value not in POINTER_TYPES:
        compiler_error("VALUE_ERROR", f"{token.value.upper()} requires a pointer.\n\n" + \
            f"Popped type:\n{t.value} {t.location}", token, current_stack=temp_stack)
    type_stack.push(TokenType.ANY, token.location)
    return type_stack

def type_check_over(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    OVER Intrinsic pushes a copy of the second element of the stack.
    Example with the stack's top element being the rightmost: a b -> a b a
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "OVER intrinsic requires two values in the stack.",
        token, current_stack=temp_stack)
    type_stack.push(t2.value, t2.location)
    type_stack.push(t1.value, t1.location)
    type_stack.push(t2.value, t2.location)
    return type_stack

def type_check_print(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop an integer from the stack and print the value of it to the stdout."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    error_message = "PRINT intrinsic requires an integer."
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", error_message, token)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", f"{error_message}\n\nPopped type:\n{t.value} {t.location}",
        token, current_stack=temp_stack)
    return type_stack

def type_check_rot(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    ROT Intrinsic rotates the top three elements of the stack so that the third becomes first.
    Example with the stack's top element being the rightmost: a b c -> b c a
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    t3 = type_stack.pop()
    if t1 is None or t2 is None or t3 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "ROT intrinsic requires three values in the stack.",
        token, current_stack=temp_stack)
    type_stack.push(t2.value, t2.location)
    type_stack.push(t1.value, t1.location)
    type_stack.push(t3.value, t3.location)
    return type_stack

def type_check_store(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    STORE variants store a value of certain type to where a pointer is pointing to.
    It takes a pointer and a value from the stack and loads the value to the pointer address.
    Different STORE variants: STORE_BYTE, STORE_WORD, STORE_DWORD, STORE_QWORD
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    required_values_str: str = f"{token.value.upper()} intrinsic requires two values on the stack, PTR and value."
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{required_values_str}", token)
    if t1.value not in POINTER_TYPES:
        compiler_error("VALUE_ERROR", f"{required_values_str}\n\n" + \
            f"Expected types:\n{TokenType.PTR}\n{TokenType.ANY}\n\n" + \
            f"Popped types:\n{t1.value} {t1.location}\n{t2.value} {t2.location}",
            token, current_stack=temp_stack)
    return type_stack

def type_check_swap(token: Token, type_stack: TypeStack) -> TypeStack:
    """
    SWAP Intrinsic swaps two top elements in the stack.
    Example with the stack's top element being the rightmost: a b -> b a
    """
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "SWAP intrinsic requires two values in the stack.",
        token, current_stack=temp_stack)
    type_stack.push(t1.value, t1.location)
    type_stack.push(t2.value, t2.location)
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
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t and t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", \
            f"The first argument of {token.value.upper()} should be the number of the syscall.\n" + \
            f"Integer types: {INTEGER_TYPES}\n\n" + \
            f"Popped type:\n{t.value} {t.location}", token, current_stack=temp_stack)
    for _ in range(param_count):
        t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} intrinsic requires {param_count+1} values in the stack.",
            token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)  # Syscall return code
    return type_stack
