from typing import List, Literal
from compiler.defs import OpType, Op, Program, Token
from compiler.utils import compiler_error

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
            if op_asm != "":
                f.write(op_asm)

    with open(asm_file, 'a') as f:
        f.write( ';; -- exit syscall\n')
        f.write( '  mov rax, sys_exit\n')
        f.write( '  mov rdi, success\n')
        f.write( '  syscall\n')
        f.close()

def get_op_asm(op: Op, program: Program) -> str:
    if op.type == OpType.BREAK:
        return get_break_asm(op, program)
    elif op.type == OpType.DO:
        return get_do_asm(op, program)
    elif op.type == OpType.DONE:
        return get_done_asm(op, program)
    elif op.type == OpType.ELIF:
        return get_elif_asm(op, program)
    elif op.type == OpType.ELSE:
        return get_else_asm(op, program)
    elif op.type == OpType.ENDIF:
        return get_endif_asm(op)
    elif op.type == OpType.IF:
        return get_if_asm()
    elif op.type == OpType.PUSH_ARRAY:
        return get_push_array_asm(op)
    elif op.type == OpType.PUSH_CSTR:
        return get_push_cstr_asm(op)
    elif op.type == OpType.PUSH_INT:
        return get_push_int_asm(op.token.value)
    elif op.type == OpType.PUSH_STR:
        return get_push_str_asm(op)
    elif op.type == OpType.WHILE:
        return get_while_asm(op)
    elif op.type == OpType.INTRINSIC:
        intrinsic: str = op.token.value.upper()
        if intrinsic == "DIV":
            return get_div_asm()
        elif intrinsic == "DIVMOD":
            return get_divmod_asm()
        elif intrinsic == "DROP":
            return get_drop_asm()
        elif intrinsic == "DUP":
            return get_dup_asm()
        elif intrinsic == "DUP2":
            return get_dup2_asm()
        elif intrinsic == "EXIT":
            return get_exit_asm()
        elif intrinsic == "EQ":
            return get_eq_asm()
        elif intrinsic == "GE":
            return get_ge_asm()
        elif intrinsic == "GET_NTH":
            return get_nth_asm()
        elif intrinsic == "GT":
            return get_gt_asm()
        elif intrinsic == "INPUT":
            return get_input_asm(op)
        elif intrinsic == "LE":
            return get_le_asm()
        elif intrinsic == "LT":
            return get_lt_asm()
        elif intrinsic == "MINUS":
            return get_minus_asm()
        elif intrinsic == "MOD":
            return get_mod_asm()
        elif intrinsic == "MUL":
            return get_mul_asm()
        elif intrinsic == "NE":
            return get_ne_asm()
        elif intrinsic == "OVER":
            return get_over_asm()
        elif intrinsic == "PLUS":
            return get_plus_asm()
        # TODO: Merge PRINT and PRINT_INT
        elif intrinsic == "PRINT":
            return get_string_output_asm(intrinsic)
        elif intrinsic == "PRINT_INT":
            return get_print_int_asm()
        elif intrinsic == "PUTS":
            return get_string_output_asm(intrinsic)
        elif intrinsic == "ROT":
            return get_rot_asm()
        elif intrinsic == "SWAP":
            return get_swap_asm()
        elif intrinsic == "SWAP2":
            return get_swap2_asm()
        elif intrinsic == "SYSCALL0":
            return get_syscall_asm(param_count=0)
        elif intrinsic == "SYSCALL1":
            return get_syscall_asm(param_count=1)
        elif intrinsic == "SYSCALL2":
            return get_syscall_asm(param_count=2)
        elif intrinsic == "SYSCALL3":
            return get_syscall_asm(param_count=3)
        elif intrinsic == "SYSCALL4":
            return get_syscall_asm(param_count=4)
        elif intrinsic == "SYSCALL5":
            return get_syscall_asm(param_count=5)
        elif intrinsic == "SYSCALL6":
            return get_syscall_asm(param_count=6)
        else:
            compiler_error("NOT_IMPLEMENTED", f"Intrinsic {intrinsic} has not been implemented.", op.token)
    else:
        compiler_error("NOT_IMPLEMENTED", f"Operation {op.type.name} has not been implemented.", op.token)

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

def get_end_op_for_while(op: Op, program: Program) -> Op:
    while_count: int = 0
    for i in range(op.id, len(program)):
        if program[i].type == OpType.DONE:
            while_count -= 1
            if while_count == 0:
                return program[i]
        if program[i].type == OpType.WHILE:
            while_count += 1
    compiler_error("AMBIGUOUS_BREAK", "WHILE loop does not have DONE.", op.token)

# Find the parent WHILE keyword
def get_parent_while(op: Op, program: Program) -> Op:
    end_count: int = 0
    for i in range(op.id - 1, -1, -1):
        if program[i].type == OpType.WHILE:
            if end_count == 0:
                return program[i]
            end_count -= 1
        if program[i].type == OpType.DONE:
            end_count += 1
    compiler_error(f"AMBIGUOUS_{op.token.value.upper()}", "BREAK operand without parent WHILE.", op.token)

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
            or ( parent_op_type == OpType.WHILE and op_type == OpType.DONE and while_count == 0):
            jump_destination: str = program[i].type.name + str(i)
            op_asm: str = generate_do_asm(jump_destination)
            break

        if parent_op_type == OpType.WHILE and op_type == OpType.DONE:
            while_count -= 1
    return op_asm

def get_parent_op_type_do(op: Op, program: Program) -> OpType:
    for i in range(op.id - 1, -1, -1):
        if program[i].type in (OpType.IF, OpType.ELIF, OpType.WHILE):
            return program[i].type
        if program[i].type in (OpType.DO, OpType.DONE, OpType.ENDIF):
            break
    compiler_error("AMBIGUOUS_DO", "DO operand without parent IF, ELIF or WHILE", op.token)

# BREAK is unconditional jump to operand after current loop's END
def get_break_asm(op: Op, program: Program) -> str:
    parent_while: Op = get_parent_while(op, program)
    parent_end:   Op = get_end_op_for_while(parent_while, program)
    return f'  jmp DONE{parent_end.id}\n'

def generate_do_asm(jump_destination: str) -> str:
    op_asm: str  =  '  pop rax\n'
    op_asm      +=  '  add rsp, 8\n'
    op_asm      +=  '  test rax, rax\n'
    op_asm      += f'  jz {jump_destination}\n'
    return op_asm

# DONE is unconditional jump to WHILE
def get_done_asm(op: Op, program: Program) -> str:
    parent_while: Op = get_parent_while(op, program)
    op_asm: str  = f'  jmp WHILE{parent_while.id}\n'
    op_asm      += f'DONE{op.id}:\n'
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

# ENDIF is a keyword for DO, ELIF or ELSE to jump to
def get_endif_asm(op: Op) -> str:
    return f'ENDIF{op.id}:\n'

# IF is like DUP, it duplicates the first element in the stack
def get_if_asm() -> str:
    return get_dup_asm()

def get_push_array_asm(op: Op) -> str:
    op_asm: str  = f'  mov rsi, s_arr{op.id} ; Pointer to array\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

def get_push_cstr_asm(op: Op) -> str:
    op_asm: str  = f'  mov rsi, cs{op.id} ; Pointer to string\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

def get_push_int_asm(integer: str) -> str:
    op_asm: str  = f'  mov rax, {integer}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_str_asm(op: Op) -> str:
    str_val: str = op.token.value[1:-1]  # Take quotes out of the string
    str_len: int = len(str_val) + 1      # Add newline
    op_asm: str  = f'  mov rax, {str_len} ; String length\n'
    op_asm      += f'  mov rsi, s{op.id} ; Pointer to string\n'
    op_asm      +=  '  push rax\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

# WHILE is a keyword for DONE to jump to.
# Also like DUP it duplicates the first element in the stack.
def get_while_asm(op: Op) -> str:
    op_asm: str  = f'WHILE{op.id}:\n'
    op_asm      += get_dup_asm()
    return op_asm

def get_div_asm() -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rax ; Quotient\n'
    return op_asm

def get_divmod_asm() -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rdx ; Remainder\n'
    op_asm      += '  push rax ; Quotient\n'
    return op_asm

def get_drop_asm(count: int = 1) -> str:
    return f'  add rsp, {8*count}\n'

def get_dup_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_dup2_asm() -> str:
    op_asm: str  = '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_exit_asm() -> str:
    op_asm: str  = '  mov rax, 60\n'
    op_asm      += '  mov rdi, 0\n'
    op_asm      += '  syscall\n'
    return op_asm

def get_eq_asm() -> str:
    return get_comparison_asm("cmove")

def get_ge_asm() -> str:
    return get_comparison_asm("cmovge")

# Copies Nth element from the stack to the top of the stack
def get_nth_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  sub rax, 1\n'
    op_asm      += '  mov rbx, 8\n'
    op_asm      += '  mul rbx\n'
    op_asm      += '  add rsp, rax ; Stack pointer to the Nth element\n'
    op_asm      += '  pop rbx      ; Get Nth element to rax\n'
    op_asm      += '  add rax, 8\n'
    op_asm      += '  sub rsp, rax ; Return stack pointer\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_gt_asm() -> str:
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
    return op_asm

def get_le_asm() -> str:
    return get_comparison_asm("cmovle")

def get_lt_asm() -> str:
    return get_comparison_asm("cmovl")

def get_minus_asm() -> str:
    return get_arithmetic_asm("sub")

def get_mod_asm() -> str:
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rdx ; Remainder\n'
    return op_asm

def get_mul_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  mul rbx\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_ne_asm() -> str:
    return get_comparison_asm("cmovne")

def get_over_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_plus_asm() -> str:
    return get_arithmetic_asm("add")

def get_print_int_asm() -> str:
    op_asm: str  = '  pop rdi\n'
    op_asm      += '  call PrintInt\n'
    return op_asm

def get_string_output_asm(intrinsic: str) -> str:
    op_asm: str  = '  pop rsi    ; *buf\n'
    op_asm      += '  pop rdx    ; count\n'

    # PRINT is the same as PUTS but without newline
    if intrinsic == 'PRINT':
        op_asm +=  '  sub rdx, 1 ; Remove newline\n'
    op_asm      += '  mov rax, sys_write\n'
    op_asm      += '  mov rdi, stdout\n'
    op_asm      += '  syscall\n'
    return op_asm

def get_rot_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rcx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rcx\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_swap_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_swap2_asm() -> str:
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rcx\n'
    op_asm      += '  pop rdx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rdx\n'
    op_asm      += '  push rcx\n'
    return op_asm

def get_syscall_asm(param_count: int) -> str:
    op_asm: str  = "  pop rax ; syscall\n"

    # Pop arguments to syscall argument registers
    argument_registers: List[str] = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']
    for i in range(param_count):
        op_asm += f"  pop {argument_registers[i]} ; {i+1}. arg\n"

    # Call the syscall and push return code to RAX
    op_asm      += "  syscall\n"
    op_asm      += "  push rax ; return code\n"
    return op_asm
