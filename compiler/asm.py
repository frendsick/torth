from typing import List, Literal
from compiler.defs import OpType, Op, Program, STACK, Token, TokenType
from compiler.utils import check_popped_value_type, compiler_error

def generate_asm(program: Program, asm_file: str) -> None:
    for op in program:
        token: Token = op.token

        if op.type in [OpType.PUSH_STR, OpType.PUSH_CSTR]:
            str_val: str = token.value[1:-1]  # Take quotes out of the string
            insert_newline: bool = op.type == OpType.PUSH_STR
            add_string_variable_asm(asm_file, str_val, op, insert_newline, op.type)

        elif op.type == OpType.PUSH_ARRAY:
            value: str = token.value
            elements: List[str] = value[value.find("(")+1:value.rfind(")")].split(',')
            # Remove whitespaces from the elements list
            elements = [element.strip().replace("'", '"') for element in elements]
            add_array_asm(asm_file, elements, op)

        elif token.value.upper() == 'INPUT':
            add_input_buffer_asm(asm_file, op)

        with open(asm_file, 'a') as f:
            f.write(get_op_comment_asm(op, op.type))
            op_asm: str = get_op_asm(op, program=program)
            # Uncomment print to see virtual stack for ops
            #print(op.token.value, STACK)
            if op_asm != "":
                f.write(op_asm)

    with open(asm_file, 'a') as f:
        f.write( ';; -- exit syscall\n')
        f.write( '  mov rax, sys_exit\n')
        f.write( '  mov rdi, success\n')
        f.write( '  syscall\n')
        f.close()

def get_op_asm(op: Op, program: Program) -> str:
    global STACK
    token: Token = op.token

    if op.type == OpType.BREAK:
        return get_break_asm(op, program)
    elif op.type == OpType.DO:
        return get_do_asm(op, program)
    elif op.type == OpType.ELIF:
        return get_elif_asm(op, program)
    elif op.type == OpType.ELSE:
        return get_else_asm(op, program)
    elif op.type == OpType.END:
        return get_end_asm(op, program)
    elif op.type == OpType.ENDIF:
        return get_endif_asm(op)
    elif op.type == OpType.IF:
        return get_if_asm(op)
    elif op.type == OpType.PUSH_ARRAY:
        return get_push_array_asm(op)
    elif op.type == OpType.PUSH_CSTR:
        return get_push_cstr_asm(op)
    elif op.type == OpType.PUSH_INT:
        return get_push_int_asm(token)
    elif op.type == OpType.PUSH_STR:
        return get_push_str_asm(op)
    elif op.type == OpType.WHILE:
        return get_while_asm(op)
    elif op.type == OpType.INTRINSIC:
        intrinsic: str = token.value.upper()
        if intrinsic == "DIV":
            return get_div_asm(op)
        elif intrinsic == "DIVMOD":
            return get_divmod_asm(op)
        elif intrinsic == "DROP":
            return get_drop_asm(op)
        elif intrinsic == "DUP":
            return get_dup_asm(op)
        elif intrinsic == "DUP2":
            return get_dup2_asm(op)
        elif intrinsic == "ENVP":
            return get_envp_asm()
        elif intrinsic == "EXIT":
            return get_exit_asm()
        elif intrinsic == "EQ":
            return get_eq_asm(op)
        elif intrinsic == "GE":
            return get_ge_asm(op)
        elif intrinsic == "GET_NTH":
            return get_nth_asm(op)
        elif intrinsic == "GT":
            return get_gt_asm(op)
        elif intrinsic == "INPUT":
            return get_input_asm(op)
        elif intrinsic == "LE":
            return get_le_asm(op)
        elif intrinsic == "LT":
            return get_lt_asm(op)
        elif intrinsic == "MINUS":
            return get_minus_asm(op)
        elif intrinsic == "MOD":
            return get_mod_asm(op)
        elif intrinsic == "MUL":
            return get_mul_asm(op)
        elif intrinsic == "NE":
            return get_ne_asm(op)
        elif intrinsic == "OVER":
            return get_over_asm(op)
        elif intrinsic == "PLUS":
            return get_plus_asm(op)
        elif intrinsic == "POW":
            return get_pow_asm(op)
        # TODO: Merge PRINT and PRINT_INT
        elif intrinsic == "PRINT":
            return get_string_output_asm(op, intrinsic)
        elif intrinsic == "PRINT_INT":
            return get_print_int_asm()
        elif intrinsic == "PUTS":
            return get_string_output_asm(op, intrinsic)
        elif intrinsic == "ROT":
            return get_rot_asm(op)
        elif intrinsic == "SWAP":
            return get_swap_asm(op)
        elif intrinsic == "SWAP2":
            return get_swap2_asm(op)
        elif intrinsic == "SYSCALL0":
            return get_syscall_asm(op, param_count=0)
        elif intrinsic == "SYSCALL1":
            return get_syscall_asm(op, param_count=1)
        elif intrinsic == "SYSCALL2":
            return get_syscall_asm(op, param_count=2)
        elif intrinsic == "SYSCALL3":
            return get_syscall_asm(op, param_count=3)
        elif intrinsic == "SYSCALL4":
            return get_syscall_asm(op, param_count=4)
        elif intrinsic == "SYSCALL5":
            return get_syscall_asm(op, param_count=5)
        elif intrinsic == "SYSCALL6":
            return get_syscall_asm(op, param_count=6)
        else:
            compiler_error(op, "NOT_IMPLEMENTED", f"Intrinsic {intrinsic} has not been implemented.")
    else:
        compiler_error(op, "NOT_IMPLEMENTED", f"Operation {op.type.name} has not been implemented.")

def get_asm_file_start() -> str:
    return '''default rel

%define buffer_len 65535 ; User input buffer length
%define stdin 0
%define stdout 1
%define success 0
%define sys_exit 60
%define sys_read 0
%define sys_write 1

section .rodata
'''

def initialize_asm(asm_file: str) -> None:
    default_asm: str = f'''{get_asm_file_start()}  formatStrInt db "%lld",10,0

section .bss
  int: RESQ 1 ; allocates 8 bytes

section .text
;; Joinked from Porth's print function, thank you Tsoding!
PrintInt:
  mov     r9, -3689348814741910323
  sub     rsp, 40
  mov     BYTE [rsp+31], 10
  lea     rcx, [rsp+30]
.L2:
  mov     rax, rdi
  lea     r8, [rsp+32]
  mul     r9
  mov     rax, rdi
  sub     r8, rcx
  shr     rdx, 3
  lea     rsi, [rdx+rdx*4]
  add     rsi, rsi
  sub     rax, rsi
  add     eax, 48
  mov     BYTE [rcx], al
  mov     rax, rdi
  mov     rdi, rdx
  mov     rdx, rcx
  sub     rcx, 1
  cmp     rax, 9
  ja      .L2
  lea     rax, [rsp+32]
  mov     edi, 1
  sub     rdx, rax
  xor     eax, eax
  lea     rsi, [rsp+32+rdx]
  mov     rdx, r8
  mov     rax, 1
  syscall
  add     rsp, 40
  ret

global _start
_start:
  mov rbp, rsp ; Initialize RBP
'''
    with open(asm_file, 'w') as f:
        f.write(default_asm)

def get_op_comment_asm(op: Op, op_type: OpType) -> str:
    src_file: str   = op.token.location[0]
    row: str        = str(op.token.location[1])
    col: str        = str(op.token.location[2])
    op_name: str    = op_type.name
    if op_name == "INTRINSIC":
        op_name = f'{op_type.name} {op.token.value}'
    return f';; -- {op_name} | File: {src_file}, Row: {row}, Col: {col}' + '\n'

# Only cmov operand changes with different comparison intrinsics
def get_comparison_asm(cmov_operand: str) -> str:
    comparison_asm: str  =  '  pop rax\n'
    comparison_asm      +=  '  pop rbx\n'
    comparison_asm      +=  '  mov rcx, 0\n'
    comparison_asm      +=  '  mov rdx, 1\n'
    comparison_asm      +=  '  cmp rax, rbx\n'
    comparison_asm      += f'  {cmov_operand} rcx, rdx\n'
    comparison_asm      +=  '  push rbx\n'
    comparison_asm      +=  '  push rcx\n'
    return comparison_asm

def get_arithmetic_asm(operand: str) -> str:
    arithmetic_asm: str  =  '  pop rbx\n'
    arithmetic_asm      +=  '  pop rax\n'
    arithmetic_asm      += f'  {operand} rax, rbx\n'
    arithmetic_asm      +=  '  push rax\n'
    return arithmetic_asm

def add_string_variable_asm(asm_file: str, string: str, op: Op, insert_newline: bool, op_type: OpType) -> None:
    with open(asm_file, 'r') as f:
        file_lines: List[str] = f.readlines()
    with open(asm_file, 'w') as f:
        if op_type == OpType.PUSH_STR:
            str_prefix: Literal['s', 'cs'] = 's'
        elif op_type == OpType.PUSH_CSTR:
            str_prefix = 'cs'
        f.write(get_asm_file_start())
        if insert_newline:
            f.write(f'  {str_prefix}{op.id} db "{string}",10,0\n')
        else:
            f.write(f'  {str_prefix}{op.id} db "{string}",0\n')

        # Rewrite lines except for the first line (section .rodata)
        len_asm_file_start: int = len(get_asm_file_start().split('\n')) - 1
        for i in range(len_asm_file_start, len(file_lines)):
            f.write(file_lines[i])

def add_array_asm(asm_file: str, array: list, op: Op) -> None:
    with open(asm_file, 'r') as f:
        file_lines: List[str] = f.readlines()
    with open(asm_file, 'w') as f:
        f.write(get_asm_file_start())
        for i in range(len(array)):
            f.write(f'  s{op.id}_{i}: db {array[i]},0\n')
        f.write(f'  s_arr{op.id}: dq ')
        for i in range(len(array)):
            f.write(f's{op.id}_{i}, ')
        f.write('0\n') # Array ends at NULL byte

        # Rewrite lines
        len_asm_file_start: int = len(get_asm_file_start().split('\n')) - 1
        for i in range(len_asm_file_start, len(file_lines)):
            f.write(file_lines[i])

def add_input_buffer_asm(asm_file: str, op: Op):
    with open(asm_file, 'r') as f:
        file_lines: List[str] = f.readlines()
    with open(asm_file, 'w') as f:
        f.write(get_asm_file_start())
        row: int = len(get_asm_file_start().splitlines()) - 1
        while row < len(file_lines):
            row += 1
            f.write(file_lines[row])
            if file_lines[row] == "section .bss\n":
                break
        f.write(f'  buffer{op.id}: resb buffer_len\n')

        # Rewrite lines
        for i in range(row+1, len(file_lines)):
            f.write(file_lines[i])

def get_stack_after_syscall(stack: List[str], param_count: int) -> List[str]:
    _syscall = stack.pop()
    for _i in range(param_count):
        stack.pop()
    stack.append('0') # Syscall return value is 0 by default
    return stack

def get_end_op_for_while(op: Op, program: Program) -> Op:
    while_count: int = 0
    for i in range(op.id, len(program)):
        if program[i].type == OpType.END:
            while_count -= 1
            if while_count == 0:
                return program[i]
        if program[i].type == OpType.WHILE:
            while_count += 1
    compiler_error(op, "AMBIGUOUS_BREAK", "WHILE loop does not have END.")

# Find the parent WHILE keyword
def get_parent_while(op: Op, program: Program) -> Op:
    end_count: int = 0
    for i in range(op.id - 1, -1, -1):
        if program[i].type == OpType.WHILE:
            if end_count == 0:
                return program[i]
            end_count -= 1
        if program[i].type == OpType.END:
            end_count += 1
    compiler_error(op, f"AMBIGUOUS_{op.token.value.upper()}", "BREAK operand without parent WHILE.")

# DO is conditional jump to operand after ELIF, ELSE, END or ENDIF
def get_do_asm(op: Op, program: Program) -> str:
    parent_op_type: OpType = get_parent_op_type_do(op, program)
    while_count: int = 0
    for i in range(op.id + 1, len(program)):
        op_type: OpType = program[i].type

        # Keep count on the nested WHILE's
        if parent_op_type == OpType.WHILE and op_type == OpType.WHILE:
            while_count += 1
            continue

        if ( parent_op_type == OpType.IF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF) ) \
            or ( parent_op_type == OpType.ELIF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF) ) \
            or ( parent_op_type == OpType.WHILE and op_type == OpType.END and while_count == 0):
            jump_destination: str = program[i].type.name + str(i)
            op_asm: str = generate_do_asm(op, jump_destination)
            break

        if parent_op_type == OpType.WHILE and op_type == OpType.END:
            while_count -= 1
    return op_asm

def get_parent_op_type_do(op: Op, program: Program) -> OpType:
    for i in range(op.id - 1, -1, -1):
        if program[i].type in (OpType.IF, OpType.ELIF, OpType.WHILE):
            return program[i].type
        if program[i].type in (OpType.DO, OpType.END, OpType.ENDIF):
            break
    compiler_error(op, "AMBIGUOUS_DO", "DO operand without parent IF, ELIF or WHILE")

# BREAK is unconditional jump to operand after current loop's END
def get_break_asm(op: Op, program: Program) -> str:
    parent_while: Op = get_parent_while(op, program)
    parent_end:   Op = get_end_op_for_while(parent_while, program)
    return f'  jmp END{parent_end.id}\n'

def generate_do_asm(jump_destination: str) -> str:
    op_asm: str  =  '  pop rax\n'
    op_asm      +=  '  add rsp, 8\n'
    op_asm      +=  '  test rax, rax\n'
    op_asm      += f'  jz {jump_destination}\n'
    return op_asm

# ELIF is unconditional jump to ENDIF and a keyword for DO to jump to
def get_elif_asm(op: Op, program: Program) -> str:
    op_asm: str = ''
    for i in range(op.id + 1, len(program)):
        if program[i].type == OpType.ENDIF:
            op_asm += f'  jmp ENDIF{i}\n'
            op_asm += f'ELIF{op.id}:\n'
            break
        # ELIF is like DUP, it duplicates the first element in the stack
    op_asm +=  '  pop rax\n'
    op_asm +=  '  push rax\n'
    op_asm +=  '  push rax\n'
    try:
        top: str = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
    STACK.append(top)
    STACK.append(top)
    return op_asm

# ELSE is unconditional jump to ENDIF and a keyword for DO to jump to
def get_else_asm(op: Op, program: Program) -> str:
    op_asm: str = ''
    for i in range(op.id + 1, len(program)):
        if program[i].type == OpType.ENDIF:
            op_asm += f'  jmp ENDIF{i}\n'
            op_asm += f'ELSE{op.id}:\n'
            break
    return op_asm

# END is unconditional jump to WHILE
def get_end_asm(op: Op, program: Program) -> str:
    parent_while: Op = get_parent_while(op, program)
    op_asm: str  = f'  jmp WHILE{parent_while.id}\n'
    op_asm      += f'END{op.id}:\n'
    return op_asm

# ENDIF is a keyword for DO, ELIF or ELSE to jump to
def get_endif_asm(op: Op) -> str:
    return f'ENDIF{op.id}:\n'

# IF is like DUP, it duplicates the first element in the stack
def get_if_asm(op: Op) -> str:
    return get_dup_asm(op)

def get_push_array_asm(op: Op) -> str:
    STACK.append(f"*buf s_arr{op.id}")
    op_asm: str  = f'  mov rsi, s_arr{op.id} ; Pointer to array\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

def get_push_cstr_asm(op: Op) -> str:
    STACK.append(f"*buf cs{op.id}")
    op_asm: str  = f'  mov rsi, cs{op.id} ; Pointer to string\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

def get_push_int_asm(token: Token) -> str:
    integer: str = token.value
    STACK.append(integer)
    op_asm: str  = f'  mov rax, {integer}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_str_asm(op: Op) -> str:
    str_val: str = op.token.value[1:-1]  # Take quotes out of the string
    str_len: int = len(str_val) + 1      # Add newline
    STACK.append(f"{str_len}")
    STACK.append(f"*buf s{op.id}")
    op_asm: str  = f'  mov rax, {str_len} ; String length\n'
    op_asm      += f'  mov rsi, s{op.id} ; Pointer to string\n'
    op_asm      +=  '  push rax\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

# WHILE is a keyword for END to jump to.
# Also like DUP it duplicates the first element in the stack.
def get_while_asm(op: Op) -> str:
    op_asm: str  = f'WHILE{op.id}:\n'
    op_asm      +=  '  pop rax\n'
    op_asm      +=  '  push rax\n'
    op_asm      +=  '  push rax\n'
    try:
        top = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
    STACK.append(top)
    STACK.append(top)
    return op_asm

def get_div_asm(op: Op) -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rax ; Quotient\n'
    try:
        a = STACK.pop()
        b = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    try:
        STACK.append(str(int(b) // int(a)))
    except ZeroDivisionError:
        compiler_error(op, "DIVISION_BY_ZERO", "Division by zero is not possible.")
    return op_asm

def get_divmod_asm(op: Op) -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rdx ; Remainder\n'
    op_asm      += '  push rax ; Quotient\n'
    try:
        a = STACK.pop()
        b = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(str(int(a)% int(b)))
    STACK.append(str(int(a)//int(b)))
    return op_asm

def get_drop_asm(op: Op) -> str:
    try:
        STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.")
    return '  add rsp, 8\n'

def get_dup_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rax\n'
    try:
        top = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
    STACK.append(top)
    STACK.append(top)
    return op_asm

def get_dup2_asm(op: Op) -> str:
    op_asm: str  = '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)
    STACK.append(b)
    return op_asm

def get_envp_asm() -> str:
    op_asm: str  = '  mov rax, [rbp+8]\n'
    op_asm      += '  push rax\n'
    STACK.append('ENVP')
    return op_asm

def get_exit_asm() -> str:
    op_asm: str  = '  mov rax, 60\n'
    op_asm      += '  mov rdi, 0\n'
    op_asm      += '  syscall\n'
    return op_asm

def get_eq_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a==b)))
    return get_comparison_asm("cmove")

def get_ge_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>=b)))
    return get_comparison_asm("cmovge")

# Copies Nth element from the stack to the top of the stack
def get_nth_asm(op: Op) -> str:
    op_asm: str = '  pop rax\n'

    # The top element in the stack is the N
    try:
        n: int = int(STACK.pop()) - 1
        if n < 0:
            raise ValueError
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

    op_asm += f'  add rsp, {n * 8} ; Stack pointer to the Nth element\n'
    op_asm +=  '  pop rax ; Get Nth element to rax\n'
    op_asm += f'  sub rsp, {n * 8 + 8} ; Return stack pointer\n'
    op_asm +=  '  push rax\n'
    STACK.append(nth_element)
    return op_asm

def get_gt_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a>b)))
    return get_comparison_asm("cmovg")

# User input is essentially a CSTR but the length is also pushed to the stack for possible printing
def get_input_asm(op: Op) -> str:
    op_asm: str  =  '  mov rax, sys_read\n'
    op_asm      +=  '  mov rdi, stdin\n'
    op_asm      += f'  mov rsi, buffer{op.id}\n'
    op_asm      +=  '  mov rdx, buffer_len\n'
    op_asm      +=  '  syscall\n'
    op_asm      +=  '  xor rdx, rdx\n'
    op_asm      += f'  mov [buffer{op.id}+rax-1], dl  ; Change newline character to NULL\n'
    op_asm      +=  '  push rax\n'
    op_asm      += f'  push buffer{op.id}\n'
    STACK.append(f"42") # User input length is not known beforehand
    STACK.append(f"*buf buffer")
    return op_asm

def get_le_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<=b)))
    return get_comparison_asm("cmovle")

def get_lt_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a<b)))
    return get_comparison_asm("cmovl")

def get_minus_asm(op: Op) -> str:
    ints: List[int] = pop_integers_from_stack(op, pop_count=2)
    STACK.append(str(int(ints[0]) + int(ints[1])))
    return get_arithmetic_asm("sub")

def get_mod_asm(op: Op) -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rdx ; Remainder\n'
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    STACK.append(str(int(a) % int(b)))
    return op_asm

def get_mul_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  mul rbx\n'
    op_asm      += '  push rax\n'
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    STACK.append(str(int(a) * int(b)))
    return op_asm

def get_ne_asm(op: Op) -> str:
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(str(int(a!=b)))
    return get_comparison_asm("cmovne")

def get_over_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    try:
        b = STACK.pop()
        a = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "The stack does not contain at least two elements.")
    check_popped_value_type(op, a, expected_type='INT')
    check_popped_value_type(op, b, expected_type='INT')
    STACK.append(a)
    STACK.append(b)
    STACK.append(a)
    return op_asm

def get_plus_asm(op: Op) -> str:
    ints: List[int] = pop_integers_from_stack(op, pop_count=2)
    STACK.append(str(int(ints[0]) + int(ints[1])))
    return get_arithmetic_asm("add")

def pop_integers_from_stack(op: Op, pop_count: int) -> List[int]:
    popped_integers: List[int] = []
    for _ in range(pop_count):
        try:
            popped: str = STACK.pop()
            check_popped_value_type(op, popped, expected_type='INT')
            popped_integers.append(int(popped))
        except IndexError:
            compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    return popped_integers

# The sequence of operations is from examples/pow.torth
# TODO: Make "POW" Macro in Torth when Macro's are implemented
def get_pow_asm(op: Op) -> str:
    do_jump_destination: str = f'END{op.id}'
    mock_int_token: Token = Token('1', TokenType.INT, op.token.location)
    op_asm: str  = get_over_asm(op)
    op_asm      += get_push_int_asm(mock_int_token)
    op_asm      += get_rot_asm(op)
    op_asm      += get_rot_asm(op)
    op_asm      += get_swap_asm(op)
    op_asm      += get_while_asm(op)
    op_asm      += get_rot_asm(op)
    op_asm      += get_over_asm(op)
    op_asm      += get_gt_asm(op)
    op_asm      += generate_do_asm(op, do_jump_destination)
    op_asm      += get_swap_asm(op)
    op_asm      += get_swap2_asm(op)
    op_asm      += get_dup_asm(op)
    op_asm      += get_rot_asm(op)
    op_asm      += get_mul_asm(op)
    op_asm      += get_swap_asm(op)
    op_asm      += get_swap2_asm(op)
    op_asm      += get_push_int_asm(mock_int_token)
    op_asm      += get_plus_asm(op)
    op_asm      += f'  jmp WHILE{op.id}\n'
    op_asm      += f'{do_jump_destination}:\n'
    for _ in range(3):
        op_asm  += get_drop_asm(op)

    try:
        exponent: str   = STACK.pop()
        number: str     = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    check_popped_value_type(op, number, expected_type='INT')
    check_popped_value_type(op, exponent, expected_type='INT')
    STACK.append(str(int(number)**int(exponent)))

    return op_asm

def get_print_int_asm() -> str:
    op_asm: str  = '  pop rdi\n'
    op_asm      += '  call PrintInt\n'
    return op_asm

def get_string_output_asm(op: Op, intrinsic: str) -> str:
    op_asm: str  = '  pop rsi    ; *buf\n'
    op_asm      += '  pop rdx    ; count\n'

    # PRINT is the same as PUTS but without newline
    if intrinsic == 'PRINT':
        op_asm +=  '  sub rdx, 1 ; Remove newline\n'
    op_asm      += '  mov rax, sys_write\n'
    op_asm      += '  mov rdi, stdout\n'
    op_asm      += '  syscall\n'
    try:
        buf    = STACK.pop()
        count  = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", \
            f"Not enough values in the stack for syscall 'write'.\n{intrinsic} operand requires two values, *buf and count.")

    # Check if the popped values were of the correct type
    check_popped_value_type(op, buf, expected_type='*buf')
    check_popped_value_type(op, count, expected_type='INT')
    return op_asm

def get_rot_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rcx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rcx\n'
    op_asm      += '  push rbx\n'
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "The stack does not contain at least three elements to rotate.")
    STACK.append(a)
    STACK.append(c)
    STACK.append(b)
    return op_asm

def get_swap_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    try:
        a = STACK.pop()
        b = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    STACK.append(a)
    STACK.append(b)
    return op_asm

def get_swap2_asm(op: Op) -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rcx\n'
    op_asm      += '  pop rdx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rdx\n'
    op_asm      += '  push rcx\n'
    try:
        a = STACK.pop()
        b = STACK.pop()
        c = STACK.pop()
        d = STACK.pop()
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    STACK.append(b)
    STACK.append(a)
    STACK.append(d)
    STACK.append(c)
    return op_asm

def get_syscall_asm(op: Op, param_count: int) -> str:
    op_asm: str  = "  pop rax ; syscall\n"

    # Pop arguments to syscall argument registers
    argument_registers: List[str] = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']
    for i in range(param_count):
        op_asm += f"  pop {argument_registers[i]} ; {i+1}. arg\n"

    # Call the syscall and push return code to RAX
    op_asm      += "  syscall\n"
    op_asm      += "  push rax ; return code\n"

    global STACK
    try:
        STACK = get_stack_after_syscall(STACK, param_count)
    except IndexError:
        compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
    return (op_asm)
