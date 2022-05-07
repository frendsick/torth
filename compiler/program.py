import subprocess
from typing import List, Tuple
from compiler.defs import Intrinsic, Op, OpType, Program, STACK, TokenType, Token
from compiler.utils import check_popped_value_type, compiler_error

def intrinsic_exists(token: str) -> bool:
    return bool(hasattr(Intrinsic, token))

def generate_program(tokens = List[Token]) -> Program:
    program: List[Op] = []
    for id, token in enumerate(tokens):
        token_value: str = token.value.upper()
        if token.type == TokenType.ARRAY:
            op_type = OpType.PUSH_ARRAY
        elif token.type == TokenType.BOOL:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.CSTR:
            op_type = OpType.PUSH_CSTR
        elif token.type == TokenType.INT:
            op_type = OpType.PUSH_INT
        elif token.type == TokenType.STR:
            op_type = OpType.PUSH_STR
        elif token_value == 'BREAK':
            op_type = OpType.BREAK
        elif token_value == 'DO':
            op_type = OpType.DO
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
        else:
            raise AttributeError (f"Operation '{token.value}' is not found")

        operand: Op = Op(id, op_type, token)
        program.append(operand)
    return program

def run_code(exe_file: str) -> None:
    subprocess.run([f'./{exe_file}'])

# Type check all operations which
def type_check_program(program: Program) -> None:
    global STACK
    NOT_TYPED_TOKENS: List[Token] = [ 'BREAK', 'ELSE', 'END', 'ENDIF', 'EXIT', 'PRINT_INT' ]
    for op in program:
        token: Token = op.token
        if token.value.upper() in NOT_TYPED_TOKENS:
            continue
        elif op.type == OpType.DO:
            type_check_do(op)
        elif op.type == OpType.ELIF:
            type_check_dup(op)  # ELIF duplicates the first element in the stack
        elif op.type == OpType.IF:
            type_check_dup(op)  # IF duplicates the first element in the stack
        elif op.type == OpType.PUSH_ARRAY:
            STACK.append(f"*buf s_arr{op.id}")
        elif op.type == OpType.PUSH_CSTR:
            STACK.append(f"*buf cs{op.id}")
        elif op.type == OpType.PUSH_INT:
            STACK.append(op.token.value)
        elif op.type == OpType.PUSH_STR:
            type_check_push_str(op)
        elif op.type == OpType.WHILE:
            type_check_dup(op)  # WHILE duplicates the first element in the stack
        elif op.type == OpType.INTRINSIC:
            intrinsic: str = token.value.upper()
            if intrinsic == "DIV":
                type_check_div(op)
            elif intrinsic == "DIVMOD":
                type_check_divmod(op)
            elif intrinsic == "DROP":
                type_check_drop(op)
            elif intrinsic == "DUP":
                type_check_dup(op)
            elif intrinsic == "DUP2":
                type_check_dup2(op)
            elif intrinsic == "ENVP":
                STACK.append('ENVP')
            elif intrinsic == "EQ":
                type_check_eq(op)
            elif intrinsic == "GE":
                type_check_ge(op)
            elif intrinsic == "GET_NTH":
                type_check_nth(op)
            elif intrinsic == "GT":
                type_check_gt(op)
            elif intrinsic == "INPUT":
                type_check_input()
            elif intrinsic == "LE":
                type_check_le(op)
            elif intrinsic == "LT":
                type_check_lt(op)
            elif intrinsic == "MINUS":
                type_check_minus(op)
            elif intrinsic == "MOD":
                type_check_mod(op)
            elif intrinsic == "MUL":
                type_check_mul(op)
            elif intrinsic == "NE":
                type_check_ne(op)
            elif intrinsic == "OVER":
                type_check_over(op)
            elif intrinsic == "PLUS":
                type_check_plus(op)
            elif intrinsic == "POW":
                continue #return type_check_pow(op)
            elif intrinsic == "PRINT":
                type_check_string_output(op, intrinsic)
            elif intrinsic == "PUTS":
                type_check_string_output(op, intrinsic)
            elif intrinsic == "ROT":
                type_check_rot(op)
            elif intrinsic == "SWAP":
                continue #return type_check_swap(op)
            elif intrinsic == "SWAP2":
                continue #return type_check_swap2(op)
            elif intrinsic == "SYSCALL0":
                continue #return type_check_syscall(op, param_count=0)
            elif intrinsic == "SYSCALL1":
                continue #return type_check_syscall(op, param_count=1)
            elif intrinsic == "SYSCALL2":
                continue #return type_check_syscall(op, param_count=2)
            elif intrinsic == "SYSCALL3":
                continue #return type_check_syscall(op, param_count=3)
            elif intrinsic == "SYSCALL4":
                continue #return type_check_syscall(op, param_count=4)
            elif intrinsic == "SYSCALL5":
                continue #return type_check_syscall(op, param_count=5)
            elif intrinsic == "SYSCALL6":
                continue #return type_check_syscall(op, param_count=6)
            else:
                compiler_error(op, "NOT_IMPLEMENTED", f"Type checking for {intrinsic} has not been implemented.")
        else:
            compiler_error(op, "NOT_IMPLEMENTED", f"Type checking for {op.type.name} has not been implemented.")
    raise NotImplementedError("Type checking is not implemented yet.")

def pop_two_from_stack(op: Op) -> Tuple[str, str]:
    try:
        b: str = STACK.pop()
        a: str = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    return a, b

def type_check_do(op: Op) -> None:
    pop_two_from_stack(op)

def type_check_push_str(op: Op) -> None:
    str_val: str = op.token.value[1:-1]  # Take quotes out of the string
    str_len: int = len(str_val) + 1      # Add newline
    STACK.append(f"{str_len}")
    STACK.append(f"*buf s{op.id}")

def type_check_div(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')

    try:
        STACK.append(str(int(b) // int(a)))
    except ZeroDivisionError:
        compiler_error(op, "DIVISION_BY_ZERO", "Division by zero is not possible.")

def type_check_divmod(op: Op) -> None:
    a, b = pop_two_from_stack(op)

    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    try:
        STACK.append(str(int(a)% int(b)))
        STACK.append(str(int(a)//int(b)))
    except ZeroDivisionError:
        compiler_error(op, "DIVISION_BY_ZERO", "Division by zero is not possible.")

def type_check_drop(op: Op) -> None:
    try:
        STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.")

def type_check_dup(op: Op) -> None:
    try:
        top = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
    STACK.append(top)
    STACK.append(top)

def type_check_dup2(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)
    STACK.append(b)

def type_check_eq(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a==b)))

def type_check_ge(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>=b)))

# Copies Nth element from the stack to the top of the stack
def type_check_nth(op: Op) -> None:
    # The top element in the stack is the N
    try:
        n: int = int(STACK.pop()) - 1
        if n < 0:
            compiler_error(op, "STACK_INDEX_ERROR", "Stack index N cannot be <= 0.")
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    except ValueError:
        compiler_error(op, "STACK_VALUE_ERROR", "First element in the stack is not a non-zero positive integer.")
    try:
        stack_index: int = len(STACK) - 1
        nth_element: str = STACK[stack_index - n]
    except IndexError:
        compiler_error(op, "NOT_ENOUGH_ELEMENTS_IN_STACK", \
                    f"Cannot get {n+1}. element from the stack: Stack only contains {len(STACK)} elements.")

    STACK.append(nth_element)

def type_check_gt(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>b)))

def type_check_input() -> None:
    STACK.append(f"42") # User input length is not known beforehand
    STACK.append(f"*buf buffer")

def type_check_le(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<=b)))

def type_check_lt(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<b)))

def type_check_minus(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(str(int(a) + int(b)))

def type_check_mod(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(str(int(a) % int(b)))

def type_check_mul(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(str(int(a) * int(b)))

def type_check_ne(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a!=b)))

def type_check_over(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)

def type_check_plus(op: Op) -> None:
    a, b = pop_two_from_stack(op)
    STACK.append(str(int(a) + int(b)))

def type_check_string_output(op: Op, intrinsic: str) -> None:
    try:
        buf    = STACK.pop()
        count  = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", \
            f"Not enough values in the stack for syscall 'write'.\n{intrinsic} operand requires two values, *buf and count.")

    check_popped_value_type(op, buf, expected_type='*buf')
    check_popped_value_type(op, count, expected_type='INT')

def type_check_rot(op: Op) -> None:
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "The stack does not contain three elements to rotate.")
    STACK.append(a)
    STACK.append(c)
    STACK.append(b)
