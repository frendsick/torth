"""
Functions for compile-time type checking and running the Torth program
"""
import subprocess
from typing import List, Tuple
from compiler.defs import Intrinsic, Memory, Op, OpType, Program
from compiler.defs import STACK, Token, TokenType, TypeStack
from compiler.utils import check_popped_value_type, compiler_error

def generate_program(tokens: List[Token], memories: List[Memory]) -> Program:
    """Generate a Program from a list of Tokens. Return the Program."""
    program: List[Op] = []
    for op_id, token in enumerate(tokens):
        token_value: str = token.value.upper()
        if token.type == TokenType.ARRAY:
            op_type = OpType.PUSH_ARRAY
        elif token.type == TokenType.BOOL:
            op_type = OpType.PUSH_INT
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
    NOT_TYPED_TOKENS: List[str] = [ 'BREAK', 'DONE', 'ELSE', 'ENDIF', 'WHILE' ]
    for op in program:
        token: Token = op.token
        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        if op.type == OpType.DO:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.ELIF:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.IF:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.PUSH_ARRAY:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.PUSH_CHAR:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.PUSH_INT:
            type_stack = type_check_push_int(type_stack)
        elif op.type == OpType.PUSH_STR:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.PUSH_PTR:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if   intrinsic == "DIVMOD":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "DROP":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "DUP":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "ENVP":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "EQ":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "GE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "GT":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "HERE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "INPUT":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "LE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "LT":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "LOAD_BYTE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "LOAD_QWORD":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "MINUS":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "MUL":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "NE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "NTH":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "OVER":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "PLUS":
                type_stack = type_check_plus(token, type_stack)
            elif intrinsic == "PRINT":
                type_stack = type_check_print(token, type_stack)
            elif intrinsic == "PUTS":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "ROT":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "STORE_BYTE":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "STORE_QWORD":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SWAP":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SWAP2":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL0":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL1":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL2":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL3":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL4":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL5":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            elif intrinsic == "SYSCALL6":
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
            else:
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

def pop_two_from_stack(token: Token) -> Tuple[str, str]:
    """Pop two items from the virtual stack and return a tuple containing those"""
    try:
        b: str = STACK.pop()
        a: str = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)
    return a, b

def type_check_do(token: Token) -> None:
    """DO Keyword pops two items from the stack"""
    pop_two_from_stack(token)

def type_check_push_int(type_stack: TypeStack) -> TypeStack:
    """Push an integer to the stack"""
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_divmod(token: Token) -> None:
    """DIV pops two items from the stack and divides second from the top one"""
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')

    try:
        STACK.append(str(int(a) %  int(b)))
        STACK.append(str(int(a) // int(b)))
    except ZeroDivisionError:
        compiler_error("DIVISION_BY_ZERO", "Division by zero is not possible.", token)

def type_check_drop(token: Token) -> None:
    """DROP removes one item from the stack."""
    try:
        STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.", token)

def type_check_dup(token: Token) -> None:
    """DUP duplicates the top element of the stack."""
    try:
        top = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.", token)
    STACK.append(top)
    STACK.append(top)

def type_check_eq(token: Token) -> None:
    """
    EQ takes two elements from the stack and checks if they are equal.
    It pushes the second element to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a==b)))

def type_check_ge(token: Token) -> None:
    """
    GE takes two elements from the stack and checks if the top element >= the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>=b)))

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

def type_check_gt(token: Token) -> None:
    """
    GT takes two elements from the stack and checks if the top element > the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>b)))

def type_check_input() -> None:
    """INPUT reads from stdin to buffer and pushes the pointer to the buffer."""
    STACK.append("*buf s_buffer")

def type_check_le(token: Token) -> None:
    """
    LE takes two elements from the stack and checks if the top element <= the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<=b)))

def type_check_lt(token: Token) -> None:
    """
    LT takes two elements from the stack and checks if the top element < the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<b)))

def type_check_load(token: Token) -> None:
    """
    LOAD variants load certain size value from where a pointer is pointing to.
    It takes one pointer from the stack and pushes back the dereferenced pointer value.
    Different LOAD variants: LOAD_BYTE, LOAD_QWORD.
    """
    try:
        ptr: str = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack is empty, PTR required.", token)
    check_popped_value_type(token, ptr, expected_type='PTR')

def type_check_minus(token: Token) -> None:
    """Pop two integers from the stack and decrement the second value from the top one."""
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) - int(b)))

def type_check_mul(token: Token) -> None:
    """Pop two integers from the stack and push the product of the two values."""
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) * int(b)))

def type_check_ne(token: Token) -> None:
    """
    NE takes two elements from the stack and checks if the values are not equal.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a!=b)))

def type_check_over(token: Token) -> None:
    """
    OVER Intrinsic pushes a copy of the element one behind the top element of the stack.
    Example with the stack's top element being the rightmost: a b -> a b a
    """
    a, b = pop_two_from_stack(token)
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)

def type_check_plus(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop two integers from the stack and push the sum of the two values."""
    t1 = type_stack.pop()
    t2 = type_stack.pop()
    if t1 != t2 != TokenType.INT:
        error_message = f"PLUS intrinsic requires two integers. Got: {t1}, {t2}"
        compiler_error("TYPE_ERROR", error_message, token)
    type_stack.push(TokenType.INT)
    return type_stack

def type_check_print(token: Token, type_stack: TypeStack) -> TypeStack:
    """Pop an integer from the stack and print the value of it to the stdout."""
    t = type_stack.pop()
    if t != TokenType.INT:
        error_message = f"PRINT intrinsic requires an integer. Got: {t}"
        compiler_error("TYPE_ERROR", error_message, token)
    return type_stack

def type_check_puts(token: Token) -> None:
    """Pop a pointer from the stack and print the null-terminated buffer to stdout."""
    string: str = STACK.pop()
    check_popped_value_type(token, string, expected_type='STR')

def type_check_rot(token: Token) -> None:
    """
    ROT Intrinsic rotates the top three elements of the stack so that the third becomes first.
    Example with the stack's top element being the rightmost: a b c -> b c a
    """
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack does not contain three elements to rotate.", token)
    STACK.append(b)
    STACK.append(a)
    STACK.append(c)

def type_check_store(token: Token) -> None:
    """
    STORE variants store certain size value from where a pointer is pointing to.
    It takes a pointer and a value from the stack and loads the value to the pointer address.
    Different STORE variants: STORE_BYTE, STORE_QWORD.
    """
    try:
        _value, ptr = pop_two_from_stack(token)
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", \
            f"{token.value.upper()} requires two values on the stack, PTR and value.", token)
    check_popped_value_type(token, ptr, expected_type='PTR')

def type_check_swap(token: Token) -> None:
    """
    SWAP Intrinsic swaps two top elements in the stack.
    Example with the stack's top element being the rightmost: a b -> b a
    """
    a, b = pop_two_from_stack(token)
    STACK.append(b)
    STACK.append(a)

def type_check_swap2(token: Token) -> None:
    """
    SWAP2 Intrinsic swaps the two pairs of two top elements in the stack.
    Example with the stack's top element being the rightmost: a b c d -> c d a b
    """
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
        d = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)
    STACK.append(b)
    STACK.append(a)
    STACK.append(d)
    STACK.append(c)

def type_check_syscall(token: Token, param_count: int) -> None:
    """
    SYSCALL intrinsic variants call a Linux syscall.
    Syscalls require different amount of arguments from 0 to 6.
    Different variants are named SYSCALL0 - SYSCALL6 by the amount of arguments.
    The different syscall constants required for RAX register can be found from lib/sys.torth.
    Naming convention (case sensitive): SYS_<syscall> - Example: SYS_write

    https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#tables
    """
    try:
        get_stack_after_syscall(STACK, param_count)
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)

def get_stack_after_syscall(stack: List[str], param_count: int) -> None:
    """
    Pop N+1 elements from the stack of SYSCALL Intrinsic variants
    where N is 2 for SYSCALL2 and 3 for SYSCALL3.
    """
    _syscall = stack.pop()
    for _i in range(param_count):
        stack.pop()
    stack.append('0') # Syscall return value is 0 if no errors occurred
