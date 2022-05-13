import subprocess
from typing import List, Tuple
from compiler.defs import Intrinsic, Memory, Op, OpType, Program, STACK, Token, TokenType
from compiler.utils import check_popped_value_type, compiler_error

def generate_program(tokens: List[Token], memories: List[Memory]) -> Program:
    program: List[Op] = []
    for op_id, token in enumerate(tokens):
        token_value: str = token.value.upper()
        if token.type == TokenType.ARRAY:
            op_type = OpType.PUSH_ARRAY
        elif token.type == TokenType.BOOL:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.HEX:
            op_type = OpType.PUSH_HEX
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

def intrinsic_exists(token: str) -> bool:
    return bool(hasattr(Intrinsic, token))

def function_name_exists(token: str, memories: List[Memory]) -> bool:
    for memory in memories:
        memory_name = memory[0]
        if memory_name.upper() == token:
            return True
    return False

def run_code(exe_file: str) -> None:
    subprocess.run([f'./{exe_file}'])

# Type check all operations which
def type_check_program(program: Program) -> None:
    global STACK
    NOT_TYPED_TOKENS: List[str] = [ 'BREAK', 'DONE', 'ELSE', 'ENDIF', 'WHILE' ]
    for op in program:
        token: Token = op.token
        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        elif op.type == OpType.DO:
            type_check_do(token)
        elif op.type == OpType.ELIF:
            type_check_dup(token)  # ELIF duplicates the first element in the stack
        elif op.type == OpType.IF:
            type_check_dup(token)  # IF duplicates the first element in the stack
        elif op.type == OpType.PUSH_ARRAY:
            STACK.append(f"*buf s_arr{op.id}")
        elif op.type == OpType.PUSH_HEX:
            STACK.append(token.value)
        elif op.type == OpType.PUSH_INT:
            STACK.append(token.value)
        elif op.type == OpType.PUSH_STR:
            STACK.append(f"*buf s_{op.id}")
        elif op.type == OpType.PUSH_PTR:
            STACK.append(f"*ptr {op.token.value}")
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if intrinsic == "DIV":
                type_check_div(token)
            elif intrinsic == "DROP":
                type_check_drop(token)
            elif intrinsic == "DUP":
                type_check_dup(token)
            elif intrinsic == "ENVP":
                STACK.append('ENVP')
            elif intrinsic == "EQ":
                type_check_eq(token)
            elif intrinsic == "EXIT":
                type_check_exit(token)
            elif intrinsic == "GE":
                type_check_ge(token)
            elif intrinsic == "GT":
                type_check_gt(token)
            elif intrinsic == "HERE":
                STACK.append(f"*buf s_{op.id}")
            elif intrinsic == "INPUT":
                type_check_input()
            elif intrinsic == "LE":
                type_check_le(token)
            elif intrinsic == "LT":
                type_check_lt(token)
            elif intrinsic == "MINUS":
                type_check_minus(token)
            elif intrinsic == "MOD":
                type_check_mod(token)
            elif intrinsic == "MUL":
                type_check_mul(token)
            elif intrinsic == "NE":
                type_check_ne(token)
            elif intrinsic == "NTH":
                type_check_nth(token)
            elif intrinsic == "OVER":
                type_check_over(token)
            elif intrinsic == "PLUS":
                type_check_plus(token)
            elif intrinsic == "PRINT":
                type_check_print(token)
            elif intrinsic == "PUTS":
                type_check_puts(token)
            elif intrinsic == "ROT":
                type_check_rot(token)
            elif intrinsic == "SWAP":
                type_check_swap(token)
            elif intrinsic == "SWAP2":
                type_check_swap2(token)
            elif intrinsic == "SYSCALL0":
                type_check_syscall(token, param_count=0)
            elif intrinsic == "SYSCALL1":
                type_check_syscall(token, param_count=1)
            elif intrinsic == "SYSCALL2":
                type_check_syscall(token, param_count=2)
            elif intrinsic == "SYSCALL3":
                type_check_syscall(token, param_count=3)
            elif intrinsic == "SYSCALL4":
                type_check_syscall(token, param_count=4)
            elif intrinsic == "SYSCALL5":
                type_check_syscall(token, param_count=5)
            elif intrinsic == "SYSCALL6":
                type_check_syscall(token, param_count=6)
            else:
                compiler_error("NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.", token)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.", token)

def pop_two_from_stack(token: Token) -> Tuple[str, str]:
    try:
        b: str = STACK.pop()
        a: str = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)
    return a, b

def type_check_do(token: Token) -> None:
    pop_two_from_stack(token)

def type_check_div(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')

    try:
        STACK.append(str(int(a) // int(b)))
    except ZeroDivisionError:
        compiler_error("DIVISION_BY_ZERO", "Division by zero is not possible.", token)

def type_check_drop(token: Token) -> None:
    try:
        STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.", token)

def type_check_dup(token: Token) -> None:
    try:
        top = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.", token)
    STACK.append(top)
    STACK.append(top)

def type_check_eq(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a==b)))

def type_check_exit(token: Token) -> None:
    check_popped_value_type(token, STACK.pop(), expected_type='INT')

def type_check_ge(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>=b)))

def type_check_nth(token: Token) -> None:
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
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>b)))

def type_check_input() -> None:
    STACK.append(f"*buf s_buffer")

def type_check_le(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<=b)))

def type_check_lt(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<b)))

def type_check_minus(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) - int(b)))

def type_check_mod(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) % int(b)))

def type_check_mul(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) * int(b)))

def type_check_ne(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    check_popped_value_type(token, a, expected_type='INT')
    check_popped_value_type(token, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a!=b)))

def type_check_over(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)

def type_check_plus(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(str(int(a) + int(b)))

def type_check_print(token: Token) -> None:
    integer: str = STACK.pop()
    check_popped_value_type(token, integer, expected_type='INT')

def type_check_puts(token: Token) -> None:
    string: str = STACK.pop()
    check_popped_value_type(token, string, expected_type='STR')

def type_check_rot(token: Token) -> None:
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "The stack does not contain three elements to rotate.", token)
    STACK.append(b)
    STACK.append(a)
    STACK.append(c)

def type_check_swap(token: Token) -> None:
    a, b = pop_two_from_stack(token)
    STACK.append(b)
    STACK.append(a)

def type_check_swap2(token: Token) -> None:
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
    try:
        get_stack_after_syscall(STACK, param_count)
    except IndexError:
        compiler_error("POP_FROM_EMPTY_STACK", "Not enough values in the stack.", token)

def get_stack_after_syscall(stack: List[str], param_count: int) -> None:
    _syscall = stack.pop()
    for _i in range(param_count):
        stack.pop()
    stack.append('0') # Syscall return value is 0 if no errors occurred
