"""
Functions for compile-time type checking and running the Torth program
"""
import itertools
import re
from copy import copy
from typing import Dict, List, Optional, Set
from compiler.defs import Binding, Constant, Function, Intrinsic, Location, Memory, Op, OpType, TypeNode
from compiler.defs import Program, Signature, Token, TokenType, TypeStack
from compiler.defs import INTEGER_TYPES, POINTER_TYPES
from compiler.utils import compiler_error, get_main_function, get_op_from_location, ordinal

def generate_program(tokens: List[Token], constants: List[Constant], \
    functions: Dict[str, Function], memories: List[Memory]) -> Program:
    """Generate a Program from a list of Tokens. Return the Program."""
    program: Program = []
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
        elif token_value == 'ASSIGN':
            op_type = OpType.ASSIGN_BIND
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
        elif token_value == 'IN':
            op_type = OpType.IN
        elif token_value == 'INT':
            op_type = OpType.CAST_INT
        elif token_value == 'PTR':
            op_type = OpType.CAST_PTR
        elif token_value == 'RETURN':
            op_type = OpType.RETURN
        elif token_value == 'STR':
            op_type = OpType.CAST_STR
        elif token_value == 'UINT8':
            op_type = OpType.CAST_UINT8
        elif token_value == 'PEEK':
            op_type = OpType.PEEK
        elif token_value == 'TAKE':
            op_type = OpType.TAKE
        elif token_value == 'WHILE':
            op_type = OpType.WHILE
        elif token.is_bound:
            if 'PEEK' in token.value.upper():
                op_type = OpType.PEEK_BIND
            elif 'TAKE' in token.value.upper():
                op_type = OpType.POP_BIND
            else:
                op_type = OpType.PUSH_BIND
            token.value = token.value.replace('_PEEK','').replace('_TAKE','')
        elif intrinsic_exists(token_value):
            op_type = OpType.INTRINSIC
        elif constant_exists(token.value, constants):
            op_type = OpType.PUSH_INT
        elif token.value in functions:
            op_type = OpType.FUNCTION_CALL
        elif memory_exists(token.value, memories):
            bindings_function: Optional[Function] = get_bindings_function(token.value, functions)
            op_type = OpType.PUSH_PTR
        else:
            compiler_error("OP_NOT_FOUND", f"Operation '{token_value}' is not found", token)

        if token.location not in tokens_function_cache:
            tokens_function_cache[token.location] = get_tokens_function(token, functions)
        func: Function = tokens_function_cache[token.location]
        if op_type == OpType.PUSH_PTR and bindings_function and \
            token.value not in func.binding:
            compiler_error("MEMORY_IN_USE",
                f"Memory '{token.value}' is already binded in '{bindings_function.name}' Function.", token)
        program.append( Op(op_id, op_type, token, func) )
    return program

def get_called_function_names_from_tokens(tokens: List[Token], functions: Dict[str, Function], \
    function_names: Set[str]) -> Set[str]:
    """Recursively get the names of functions from each Function's Tokens"""
    for token in tokens:
        if token.value in functions and token.value not in function_names:
            function_names.add(token.value)
            function_names = get_called_function_names_from_tokens(
                functions[token.value].tokens, functions, function_names
            )
    return function_names

def get_called_function_names(functions: Dict[str, Function]) -> Set[str]:
    """Get the names of functions that are called in code"""
    main_function: Function = get_main_function(functions)
    return get_called_function_names_from_tokens(
        main_function.tokens, functions, {main_function.name}
    )

def get_sub_programs(functions: Dict[str, Function], \
    constants: List[Constant], memories: List[Memory]) -> Dict[str, Program]:
    """
    Generate a sub-program dictionary from Functions.
    Key:    Function name
    Value:  Sub-program
    """
    sub_programs: Dict[str, Program] = {}
    called_functions: Set[str] = get_called_function_names(functions)
    for func in functions.values():
        if func.name in called_functions:
            sub_programs[func.name] = generate_program(func.tokens, constants, functions, memories)
    return sub_programs

def get_tokens_function(token: Token, functions: Dict[str, Function]) -> Function:
    """Determine the corresponding function for a Token"""
    for func in functions.values():
        for func_token in func.tokens:
            if token.location == func_token.location:
                return func
    compiler_error("COMPILER_ERROR", \
        f"Could not determine corresponding Function for Token '{token.value}'", token)

def intrinsic_exists(token_value: str) -> bool:
    """Return boolean value whether or not certain Intrinsic exists."""
    return bool(hasattr(Intrinsic, token_value))

def constant_exists(token_value: str, constants: List[Constant]) -> bool:
    """Return boolean value whether or not certain Constant exists."""
    return any(const.name == token_value for const in constants)

def memory_exists(token_value: str, memories: List[Memory]) -> bool:
    """Return boolean value whether or not certain Memory exists."""
    return any(memory.name == token_value for memory in memories)

def get_bindings_function(token_value: str, functions: Dict[str, Function]) -> Optional[Function]:
    """Get the Function in which certain Binding was created"""
    return next((func for func in functions.values() if token_value in func.binding), None)

def get_function_type_stack(func: Function) -> TypeStack:
    """Generate TypeStack from Function parameter types"""
    # Put values to the stack in the reversed order
    param_types: List[TokenType] = func.signature[0][::-1]
    param_stack: TypeStack = TypeStack()
    for param_type in param_types:
        param_stack.push(param_type, func.tokens[0].location)
    return param_stack

def type_check_program(func: Function, program: Program, functions: Dict[str, Function]) -> None:
    """
    Type check all Operands of the Program.
    Raise compiler error if the type checking fails.
    """
    if not func.tokens:
        if matching_type_lists(func.signature[0], func.signature[1]):
            return
        compiler_error("FUNCTION_SIGNATURE_ERROR",
            f"Empty function '{func.name}' with different parameter and return types.")

    branched_stacks: List[TypeStack] = [get_function_type_stack(func)]
    NOT_TYPED_TOKENS: List[str]      = [ 'BREAK', 'CONTINUE', 'PEEK', 'TAKE', 'WHILE' ]

    # Save the stack after previous IF / ELIF statements in the IF block to make it possible
    # to type check IF-ELIF chains with different stack layouts than what it was before the block.
    # This is important when there is ELSE present because then we know that the ELSE block will be
    # executed if the previous IF / ELIF conditions were not matched.
    if_block_return_stacks: List[TypeStack] = [TypeStack()]

    # Save the stack at the beginning of the IF block to enable altering the stack state during IF block.
    # This is a list of stacks to enable nested IF blocks.
    if_block_original_stacks: List[TypeStack] = [TypeStack()]

    # Track if there was an ELSE clause in the IF block.
    # Required for type checking IF blocks with each IF / ELIF keyword altering the stack state.
    else_present: bool   = False
    return_present: bool = False

    # Save the Bindings of the function to get the type of the Binding later when used
    binding: Binding = {}
    peek_count: int = 0 # Used for type checking PEEK blocks with multiple values

    for op in program:
        token: Token = op.token
        type_stack: TypeStack = branched_stacks[-1]

        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        if op.type == OpType.ASSIGN_BIND:
            type_check_assign_bind(op, type_stack, program, binding)
        elif op.type == OpType.CAST_BOOL:
            type_check_cast_bool(token, type_stack)
        elif op.type == OpType.CAST_CHAR:
            type_check_cast_char(token, type_stack)
        elif op.type == OpType.CAST_INT:
            type_check_cast_int(token, type_stack)
        elif op.type == OpType.CAST_PTR:
            type_check_cast_ptr(token, type_stack)
        elif op.type == OpType.CAST_STR:
            type_check_cast_str(token, type_stack)
        elif op.type == OpType.CAST_UINT8:
            type_check_cast_uint8(token, type_stack)
        elif op.type == OpType.DO:
            type_check_do(token, type_stack, branched_stacks)
        elif op.type == OpType.DONE:
            type_check_end_of_branch(token, branched_stacks)
        elif op.type == OpType.ELIF:
            return_present = False
            type_check_elif(token, type_stack, branched_stacks, if_block_return_stacks[-1])
        elif op.type == OpType.ELSE:
            else_present = True
            type_check_else(
                token, type_stack, branched_stacks,
                if_block_return_stacks[-1], if_block_original_stacks[-1]
            )
        elif op.type == OpType.ENDIF:
            type_check_endif(
                op, type_stack, branched_stacks,
                if_block_return_stacks, if_block_original_stacks,
                (else_present or return_present)
            )
            else_present = False
        elif op.type == OpType.FUNCTION_CALL:
            type_check_function_call(op, type_stack, functions)
        elif op.type == OpType.IF:
            return_present = False
            if_block_original_stacks.append(copy(type_stack))
            if_block_return_stacks.append(TypeStack())
        elif op.type == OpType.IN:
            peek_count = 0
        elif op.type == OpType.PEEK_BIND:
            peek_count += 1
            type_check_peek_bind(token, type_stack, binding, peek_count)
        elif op.type == OpType.POP_BIND:
            type_check_pop_bind(token, type_stack, binding)
        elif op.type == OpType.PUSH_BIND:
            type_check_push_bind(token, type_stack, binding)
        elif op.type == OpType.PUSH_BOOL:
            type_check_push_bool(token, type_stack)
        elif op.type == OpType.PUSH_CHAR:
            type_check_push_char(token, type_stack)
        elif op.type == OpType.PUSH_INT:
            type_check_push_int(token, type_stack)
        elif op.type == OpType.PUSH_PTR:
            type_check_push_ptr(token, type_stack)
        elif op.type == OpType.PUSH_STR:
            type_check_push_str(token, type_stack)
        elif op.type == OpType.PUSH_UINT8:
            type_check_push_uint8(token, type_stack)
        elif op.type == OpType.RETURN:
            return_present = True
            if_block_stack: TypeStack = if_block_return_stacks[-1] if if_block_return_stacks[-1].head \
                else if_block_original_stacks[-1]
            branched_stacks[-1] = type_check_return(op, type_stack, if_block_stack)
        elif op.type == OpType.INTRINSIC:
            type_check_intrinsic(token, type_stack, program)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

    # There should be one INT in the stack when the program ends.
    if func.name.upper() == 'MAIN':
        if type_stack.get_types() == [TokenType.INT]:
            return
        compiler_error("FUNCTION_SIGNATURE_ERROR", \
            "Only the integer return value of the program should be in the stack when program exits.\n\n" + \
            f"Stack after the MAIN function:\n{type_stack.repr()}", func.tokens[-1])

    if not correct_return_types(func, branched_stacks[-1]):
        compiler_error("FUNCTION_SIGNATURE_ERROR",
            f"Function '{func.name}' does not return the types indicated in the function signature.\n\n" + \
            f"Function parameter types: {func.signature[0]}\n" + \
            f"Function return types:    {func.signature[1]}\n",
            func.tokens[-1], branched_stacks[-1], get_function_type_stack(func))

def type_check_else(token: Token, type_stack: TypeStack, branched_stacks: List[TypeStack], \
    if_block_return_stack: Optional[TypeStack], if_block_original_stack: Optional[TypeStack]) -> None:
    """ELSE is the final section of an IF block"""
    # Save the state of the stack after the first part of the IF block
    if not if_block_return_stack.head:
        if_block_return_stack = copy(type_stack)

    type_check_end_of_branch(token, branched_stacks, \
        if_block_return_stack=if_block_return_stack)

    # Use IF block's original stack as the old stack
    branched_stacks.append(if_block_original_stack)

def type_check_intrinsic(token: Token, type_stack: TypeStack, program: Program) -> None:
    """Type check an Intrinsic. Raise compiler error if the type checking fails."""
    intrinsic: str = token.value.upper()
    if intrinsic == "AND":
        return type_check_bitwise(token, type_stack)
    if intrinsic == "ARGC":
        return type_check_push_int(token, type_stack)
    if intrinsic == "ARGV":
        return type_check_push_ptr(token, type_stack)
    if intrinsic == "DIVMOD":
        return type_check_divmod(token, type_stack)
    if intrinsic == "DROP":
        return type_check_drop(token, type_stack)
    if intrinsic == "DUP":
        return type_check_dup(token, type_stack)
    if intrinsic == "ENVP":
        return type_check_push_ptr(token, type_stack)
    if intrinsic in {"EQ", "GE", "GT", "LE", "LT", "NE"}:
        return type_check_comparison(token, type_stack)
    if intrinsic.startswith("LOAD_"):
        return type_check_load(token, type_stack)
    if intrinsic == "MINUS":
        return type_check_calculations(token, type_stack)
    if intrinsic == "MUL":
        return type_check_calculations(token, type_stack)
    if intrinsic == "NTH":
        return type_check_nth(token, type_stack, program)
    if intrinsic == "OR":
        return type_check_bitwise(token, type_stack)
    if intrinsic == "OVER":
        return type_check_over(token, type_stack)
    if intrinsic == "PLUS":
        return type_check_calculations(token, type_stack)
    if intrinsic == "PRINT":
        return type_check_print(token, type_stack)
    if intrinsic == "ROT":
        return type_check_rot(token, type_stack)
    if intrinsic.startswith("STORE_"):
        return type_check_store(token, type_stack)
    if intrinsic == "SWAP":
        return type_check_swap(token, type_stack)
    if re.fullmatch(r'SYSCALL[0-6]', intrinsic):
        return type_check_syscall(token, type_stack, int(intrinsic[-1]))
    compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)

def correct_return_types(func: Function, type_stack: TypeStack) -> bool:
    """Check if the state of TypeStack is correct after executing the Function"""
    temp_stack: TypeStack = get_function_type_stack(func)
    # Pop parameters
    for _ in func.signature[0]:
        temp_stack.pop()
    # Push return types
    for token_type in func.signature[1]:
        temp_stack.push(token_type, func.tokens[0].location)
    return matching_type_lists(
        temp_stack.get_types(),
        type_stack.get_types()
    )

def type_check_function_call(op: Op, type_stack: TypeStack, functions: Dict[str, Function]) -> None:
    """
    Type check the function parameter types.
    Returns the types in stack when the parameters are popped out.
    """
    function_signature: Signature = functions[op.token.value].signature
    param_types:  List[TokenType] = function_signature[0]
    return_types: List[TokenType] = function_signature[1]
    temp_stack: TypeStack = copy(type_stack)
    # Pop param types
    for expected_type in param_types:
        if not type_stack.head:
            compiler_error("FUNCTION_SIGNATURE_ERROR",
                f"Not enough parameters for '{op.token.value}' function\n" + \
                f"Expected types: {param_types}", op.token,
            original_stack=temp_stack)
        popped_type: TokenType = type_stack.pop().value  # type: ignore
        if not matching_types(popped_type, expected_type):
            compiler_error("FUNCTION_SIGNATURE_ERROR",
                f"Wrong type of parameter in stack for '{op.token.value}' function\n" + \
                f"Expected types: {param_types}", op.token,
            original_stack=temp_stack)
    # Push return types
    for token_type in return_types:
        type_stack.push(token_type, op.token.location)

def matching_types(type1: TokenType, type2: TokenType) -> bool:
    """Check if two types are similar"""
    return type1 == type2 or TokenType.ANY in {type1, type2}

def matching_type_lists(stack1: List[TokenType], stack2: List[TokenType]) -> bool:
    """Check if two TokenType lists have matching types in them."""
    return len(stack1) == len(stack2) and all(matching_types(type1, type2) \
        for type1, type2 in itertools.zip_longest(stack1, stack2))

def type_check_end_of_branch(token: Token, branched_stacks: List[TypeStack], \
    if_block_return_stack: Optional[TypeStack] = None) -> None:
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
        if not matching_type_lists(return_types, after_types):
            error: str   =  "Stack state should be the same after each section in the IF block.\n\n"
            error       += f"Stack state after previous sections:\n{if_block_return_stack.repr()}\n"
            error       += f"Stack state after the current section:\n{stack_after_branch.repr()}"
            compiler_error("DIFFERENT_STACK_BETWEEN_SECTIONS", error, token)
        return

    # Check for different stack states before and after the block
    error  = "Stack state should be the same after the block whether or not the condition was matched.\n\n"
    error += f"Stack state at the start of the block:\n{branched_stacks[-1].repr()}\n"
    error += f"Stack state at the end of the block:\n{stack_after_branch.repr()}"
    if len(before_types) != len(after_types):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)
    if not matching_type_lists(before_types, after_types):
        compiler_error("DIFFERENT_STACK_BETWEEN_BRANCHES", error, token)

def type_check_assign_bind(op: Op, type_stack: TypeStack, program: Program, binding: Binding) -> None:
    """ASSIGN_BIND assigns a value to existing named bound Memory"""
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", "ASSIGN keyword requires two values of the same type in the stack.",
            op.token, current_stack=temp_stack)

    bound_token: Token = get_op_from_location(t1.location, program).token
    if not bound_token.is_bound:
        compiler_error("VALUE_ERROR", "ASSIGN keyword requires a bound Memory in the top of the stack.",
            op.token, current_stack=temp_stack)

    bound_type: TokenType = binding[bound_token.value]
    if t2.value != bound_type:
        compiler_error("VALUE_ERROR",
            f"Cannot assign {t2.value.name} to bound Memory '{bound_token.value}' of type {bound_type.name}.",
            op.token, current_stack=temp_stack)

def type_check_cast_bool(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped type:\n{t.value.name} {t.location}", token, current_stack=temp_stack)
    type_stack.push(TokenType.BOOL, token.location)

def type_check_cast_char(token: Token, type_stack: TypeStack) -> None:
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

def type_check_cast_int(token: Token, type_stack: TypeStack) -> None:
    """CAST_INT explicitely casts the top element of the stack to INT type."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    type_stack.push(TokenType.INT, token.location)

def type_check_cast_ptr(token: Token, type_stack: TypeStack) -> None:
    """CAST_PTR explicitely casts the top element of the stack to PTR type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value in {TokenType.BOOL, TokenType.CHAR}:
        compiler_error("VALUE_ERROR", f"{t.value.name} cannot be cast to PTR.", token, current_stack=temp_stack)
    type_stack.push(TokenType.PTR, token.location)

def type_check_cast_str(token: Token, type_stack: TypeStack) -> None:
    """CAST_STR explicitely casts the top element of the stack to STR type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value not in POINTER_TYPES:
        compiler_error("VALUE_ERROR", "Only pointer-like values can be cast to STR.", token, current_stack=temp_stack)
    type_stack.push(TokenType.STR, token.location)

def type_check_cast_uint8(token: Token, type_stack: TypeStack) -> None:
    """CAST_UINT8 explicitely casts the top element of the stack to UINT8 type."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty.", token)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", "Only integer-like values can be cast to UINT8.", token, current_stack=temp_stack)
    type_stack.push(TokenType.UINT8, token.location)

def type_check_do(token: Token, type_stack: TypeStack, branched_stacks: List[TypeStack]) -> None:
    """DO Keyword pops one boolean from the stack"""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "DO requires two values to the stack.", token)
    if t.value not in { TokenType.BOOL, TokenType.ANY }:
        compiler_error("VALUE_ERROR", "DO requires a boolean.\n\n" + \
            f"Popped types:\n{t.value.name} {t.location}", token, current_stack=temp_stack)

    type_stack = copy(type_stack)
    branched_stacks.append(type_stack)

def type_check_elif(token: Token, type_stack: TypeStack, \
    branched_stacks: List[TypeStack], if_block_return_stack: Optional[TypeStack]) -> None:
    """Type check ELIF Keyword."""
    # Save the state of the stack after the first part of the IF block
    if not if_block_return_stack.head:
        if_block_return_stack = copy(type_stack)

    # Type check ELIF as the possible end for the IF block
    type_check_end_of_branch(token, branched_stacks,
        if_block_return_stack=if_block_return_stack)

def type_check_endif(op: Op, type_stack: TypeStack, \
    branched_stacks: List[TypeStack], if_block_return_stacks: List[TypeStack], \
    if_block_original_stacks: List[TypeStack], else_or_return_present: bool) -> None:
    """
    ENDIF ends the IF block.
    We have to check that the stack state was not altered inside the block.

    If stack state was changed, the changes should be consistent in all of the sections
    AND there should be an ELSE keyword present to act as default branch.
    """
    # Save the state of the stack after the first part of the IF block
    if not if_block_return_stacks[-1].head:
        if_block_return_stacks[-1] = copy(type_stack)

    # Type check the endif as the end of the IF block
    type_check_end_of_branch(op.token, branched_stacks, \
        if_block_return_stack=if_block_return_stacks[-1])

    # If IF block altered the stack state there MUST be an ELSE to catch all errors
    # and the IF block's return stack must match with all of the sections in the block
    if not else_or_return_present and if_block_return_stacks[-1].head and \
        not matching_type_lists(branched_stacks[-1].get_types(), if_block_return_stacks[-1].get_types()):
        compiler_error("SYNTAX_ERROR", \
            "The stack state should be the same than at the start of the IF-block.\n" + \
            "Introduce an ELSE-block if you need to return different values from IF-blocks.\n" + \
            "The stack state should be the same with every branch of the block.\n\n" + \
            f"Stack state after the previous sections in the IF block:\n{if_block_return_stacks[-1].repr()}\n"+ \
            f"The stack state before the IF block:\n{branched_stacks[-1].repr()}", op.token)

    # Make the IF block's return stack the new stack for the program
    if if_block_return_stacks[-1].head:
        branched_stacks[-1] = if_block_return_stacks[-1]

    # Reset IF-block variables
    if_block_original_stacks.pop()
    if_block_return_stacks.pop()

def type_check_peek_bind(token: Token, type_stack: TypeStack,
    binding: Binding, peek_count: int) -> None:
    """Copy the Nth item from the stack to a named Memory."""
    temp_stack: TypeStack = copy(type_stack)

    # Get the Nth value from the stack, based on peek_count
    for _ in range(peek_count):
        t = temp_stack.pop()

    if t is None:
        compiler_error("NOT_ENOUGH_VALUES_IN_STACK",
            f"Could not peek {peek_count} values from the stack because there is not enough values.",
            token, current_stack=type_stack)

    # Save the type of Nth value in the stack
    binding[token.value] = t.value

def type_check_pop_bind(token: Token, type_stack: TypeStack, binding: Binding) -> None:
    """Pop a value from the stack to a bound Memory"""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.", token)
    binding[token.value] = t.value

def type_check_push_bind(token: Token, type_stack: TypeStack, binding: Binding) -> None:
    """Push a value from bound Memory the stack"""
    type_stack.push(binding[token.value], token.location)

def type_check_push_bool(token: Token, type_stack: TypeStack) -> None:
    """Push a boolean to the stack"""
    type_stack.push(TokenType.BOOL, token.location)

def type_check_push_char(token: Token, type_stack: TypeStack) -> None:
    """Push a character to the stack"""
    type_stack.push(TokenType.CHAR, token.location)

def type_check_push_int(token: Token, type_stack: TypeStack) -> None:
    """Push an integer to the stack"""
    type_stack.push(TokenType.INT, token.location)

def type_check_push_ptr(token: Token, type_stack: TypeStack) -> None:
    """Push a pointer to the stack"""
    type_stack.push(TokenType.PTR, token.location)

def type_check_push_str(token: Token, type_stack: TypeStack) -> None:
    """Push a string to the stack"""
    type_stack.push(TokenType.STR, token.location)

def type_check_push_uint8(token: Token, type_stack: TypeStack) -> None:
    """Push an unsigned 8-bit integer to the stack"""
    type_stack.push(TokenType.UINT8, token.location)

def type_check_return(op: Op, type_stack: TypeStack, if_block_return_stack: TypeStack) -> TypeStack:
    """Return from the current Function. Function's TypeStack should be empty."""
    return_types: List[TokenType] = op.func.signature[1]
    if not matching_type_lists(type_stack.get_types(), return_types):
        compiler_error("FUNCTION_SIGNATURE_ERROR",
        f"Stack state does not match with the return types of '{op.func.name}' function.\n\n" + \
        f"Expected return types: {return_types}\n", op.token,
        current_stack=type_stack)
    return copy(if_block_return_stack)

def type_check_bitwise(token: Token, type_stack: TypeStack) -> None:
    """AND performs bitwise-AND operation to two integers."""
    temp_stack: TypeStack = copy(type_stack)
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 is None or t2 is None:
        compiler_error("POP_FROM_EMPTY_STACK", f"{token.value} intrinsic requires two integers.", token)
    if t1.value not in INTEGER_TYPES or t2.value not in INTEGER_TYPES:
        error_message = f"{token.value} intrinsic requires two integers.\n\n" + \
            f"Popped types:\n{t1.value.name} {t1.location}\n{t2.value.name} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)

def type_check_calculations(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped types:\n{t1.value.name} {t1.location}\n{t2.value.name} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)

    type_stack.push(TokenType.INT, token.location)

def type_check_comparison(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped types:\n{t1.value.name} {t1.location}\n{t2.value.name} {t2.location}"
        compiler_error("TYPE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.BOOL, token.location)

def type_check_divmod(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped types:\n{t1.value.name} {t1.location}\n{t2.value.name} {t2.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)
    type_stack.push(TokenType.INT, token.location)

def type_check_drop(token: Token, type_stack: TypeStack) -> None:
    """DROP removes one item from the stack."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.", token)

def type_check_dup(token: Token, type_stack: TypeStack) -> None:
    """DUP duplicates the top item from the stack."""
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.", token)
    type_stack.push(t.value, t.location)
    type_stack.push(t.value, t.location)

def type_check_nth(token: Token, type_stack: TypeStack, program: Program) -> None:
    """
    NTH pops one integer from the stack and pushes the Nth element from stack back to stack.
    Note that the Nth is counted without the popped integer.
    Example: 30 20 10 3 NTH print  // Output: 30 (because 30 is 3rd element without the popped 3).
    """
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", "NTH intrinsic requires an integer.", token)
    if t.value != TokenType.INT:
        error_message = "NTH intrinsic requires an integer.\n\n" + \
            f"Popped type:\n{t.value.name} {t.location}"
        compiler_error("VALUE_ERROR", error_message, token, current_stack=temp_stack)

    # Get the type of the Nth value in the stack
    nth_token: Token = get_op_from_location(t.location, program).token
    try:
        n: int = int(nth_token.value)   # Regular integer
    except ValueError:
        n = int(nth_token.value, 16)    # Hexadecimal
    for _ in range(n+1):
        popped: Optional[TypeNode] = temp_stack.pop()

    if popped is None:
        compiler_error("NOT_ENOUGH_VALUES_IN_STACK",
            f"Cannot get {ordinal(n)} value from the stack because there is not enough values.",
            token, current_stack=type_stack)
    type_stack.push(popped.value, token.location)

def type_check_load(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped type:\n{t.value.name} {t.location}", token, current_stack=temp_stack)
    type_stack.push(TokenType.ANY, token.location)

def type_check_over(token: Token, type_stack: TypeStack) -> None:
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

def type_check_print(token: Token, type_stack: TypeStack) -> None:
    """Pop an integer from the stack and print the value of it to the stdout."""
    temp_stack: TypeStack = copy(type_stack)
    t = type_stack.pop()
    error_message = "PRINT intrinsic requires an integer."
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", error_message, token)
    if t.value not in INTEGER_TYPES:
        compiler_error("VALUE_ERROR", f"{error_message}\n\nPopped type:\n{t.value.name} {t.location}",
        token, current_stack=temp_stack)

def type_check_rot(token: Token, type_stack: TypeStack) -> None:
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

def type_check_store(token: Token, type_stack: TypeStack) -> None:
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
            f"Popped types:\n{t1.value.name} {t1.location}\n{t2.value.name} {t2.location}",
            token, current_stack=temp_stack)

def type_check_swap(token: Token, type_stack: TypeStack) -> None:
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

def type_check_syscall(token: Token, type_stack: TypeStack, param_count: int) -> None:
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
            f"Popped type:\n{t.value.name} {t.location}", token, current_stack=temp_stack)
    for _ in range(param_count):
        t = type_stack.pop()
    if t is None:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} intrinsic requires {param_count+1} values in the stack.",
            token, current_stack=temp_stack)
    type_stack.push(TokenType.INT, token.location)  # Syscall return code
