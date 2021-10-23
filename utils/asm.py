import re
import subprocess
import sys
from typing import List
from utils.defs import Colors, OpType, Op, Token, Program, STACK, REGEX, MEMORY_SIZE

def get_asm_file_start(asm_file:str) -> str:
    return '''default rel
extern printf

%define sys_exit 60
%define sys_read 0
%define sys_write 1

%define stdin 0
%define stdout 1

%define success 0

section .rodata
'''

def initialize_asm(asm_file: str) -> None:
    default_asm = get_asm_file_start(asm_file) + f'''  formatStrInt db "%d",10,0

section .bss
  int: RESQ 1 ; allocates 8 bytes
  mem: RESB {MEMORY_SIZE} ; allocates {MEMORY_SIZE} bytes

section .text
PrintInt:
  global _start
  mov rsi, [rsp+8]
  mov rdi, formatStrInt
  mov rax, 0
  call printf
  ret

global main
main:
'''
    with open(asm_file, 'w') as f:
        f.write(default_asm)

def get_op_comment_asm(op: Op, op_type: OpType) -> str:
    src_file    = op.token.location[0]
    row         = str(op.token.location[1])
    col         = str(op.token.location[2])
    op_name     = op_type.name
    if op_name == "INTRINSIC":
        op_name = op_type.name + " " + op.token.value
    return ';; -- ' + op_name + ' | File: ' + src_file + ', Row: ' + row + ', Col: ' + col + '\n'

# Only cmov operand changes with different comparison intrinsics
def get_comparison_asm(cmov_operand: str) -> str:
    comparison_asm  =  '  pop rax\n'
    comparison_asm +=  '  pop rbx\n'
    comparison_asm +=  '  mov rcx, 0\n'
    comparison_asm +=  '  mov rdx, 1\n'
    comparison_asm +=  '  cmp rax, rbx\n'
    comparison_asm += f'  {cmov_operand} rcx, rdx\n'
    comparison_asm +=  '  push rcx\n'
    return comparison_asm

def get_arithmetic_asm(operand: str) -> str:
    arithmetic_asm  =  '  pop rax\n'
    arithmetic_asm +=  '  pop rbx\n'
    arithmetic_asm += f'  {operand} rax, rbx\n'
    arithmetic_asm +=  '  push rax\n'
    return arithmetic_asm

def add_string_variable_asm(asm_file: str, string: str, op: Op) -> None:
    with open(asm_file, 'r') as f:
        file_lines = f.readlines()
    with open(asm_file, 'w') as f:
        f.write(get_asm_file_start(asm_file))
        f.write(f'  s{op.id} db "{string}",10\n')

        # Rewrite lines except for the first line (section .rodata)
        len_asm_file_start = len(get_asm_file_start(asm_file).split('\n')) - 1
        for i in range(len_asm_file_start, len(file_lines)):
            f.write(file_lines[i])

def get_stack_after_syscall(stack: List[Token], param_count: int) -> List[Token]:
    syscall = stack.pop()
    for _i in range(param_count):
        stack.pop()
    syscall.value = '0' # Syscall return value is 0 by default
    stack.append(syscall)
    return stack

def compiler_error(op: Op, error_type: str, error_message: str) -> None:
    operand = op.token.value
    file    = op.token.location[0]
    row     = op.token.location[1]
    col     = op.token.location[2]

    print(Colors.HEADER + "Compiler error " + Colors.FAIL + error_type + Colors.NC + f":\n{error_message}\n")
    print(Colors.HEADER + "Operand" + Colors.NC + f": {operand}")
    print(Colors.HEADER + "File" + Colors.NC + f": {file}")
    print(Colors.HEADER + "Row" + Colors.NC + f": {row}, " \
        + Colors.HEADER + "Column" + Colors.NC + f": {col}")
    exit(1)

def check_popped_value_type(op: Op, popped_value: str, expected_type: str) -> None:
    regex = REGEX[expected_type]
    error_message = f"Wrong type of value popped from the stack.\n\n" + \
        f"{Colors.HEADER}Value{Colors.NC}: {popped_value}\n" + \
        f"{Colors.HEADER}Expected{Colors.NC}: {expected_type}\n" + \
        f"{Colors.HEADER}Regex{Colors.NC}: {regex}"

    # Raise compiler error if the value gotten from the stack does not match with the regex
    assert re.match(regex, str(popped_value)), compiler_error(op, "REGISTER_VALUE_ERROR", error_message)

def get_op_asm(op: Op, program: Program) -> str:
    global STACK
    token  = op.token
    op_asm = ""
    if op.type == OpType.END:
        offset = 0
        for i in range(op.id - 1, -1, -1):
            if program[i].type == OpType.WHILE:
                op_asm += f'  jmp {offset}\n'
                break
            offset += program[i].size
            print(f"{program[i]=}")
            print(f"{offset=}")
    elif op.type == OpType.IF:
        offset = 0
        for i in range(op.id + 1, len(program)):
            offset += program[i].size
            print(f"{program[i]=}")
            print(f"{offset=}")
            # IF is conditional jump to operand after END
            if program[i].type == OpType.END:
                break
        op_asm += f'  pop rax\n'
        op_asm += f'  push rax\n'
        op_asm += f'  test rax, rax\n'
        op_asm += f'  jz {offset}\n'
    elif op.type == OpType.PUSH_INT:
        integer = token.value
        STACK.append(integer)
        op_asm += f'  mov rax, {integer}\n'
        op_asm +=  '  push rax\n'
    elif op.type == OpType.PUSH_STR:
        str_val = op.token.value[1:-1]  # Take quotes out of the string
        str_len = len(str_val) + 1      # Add newline
        STACK.append(f"{str_len}")
        STACK.append(f"*buf s{op.id}")
        op_asm += f'  mov rax, {str_len} ; String length\n'
        op_asm += f'  mov rsi, s{op.id} ; Pointer to string\n'
        op_asm +=  '  push rax\n'
        op_asm +=  '  push rsi\n'
    elif op.type == OpType.INTRINSIC:
        intrinsic = token.value.upper()
        if intrinsic == "ARGC":
            argc = len(sys.argv)
            STACK.append(argc)
            op_asm += f'  push {argc}\n'
        elif intrinsic == "DIV":
            op_asm +=  '  xor edx, edx ; Do not use floating point arithmetic\n'
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  div rbx\n'
            op_asm +=  '  push RAX ; Quotient\n'
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(int(a.value) // int(b.value))
        elif intrinsic == "DIVMOD":
            op_asm +=  '  xor edx, edx ; Do not use floating point arithmetic\n'
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  div rbx\n'
            op_asm +=  '  push rdx ; Remainder\n'
            op_asm +=  '  push rax ; Quotient\n'
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a)% int(b)))
            STACK.append(str(int(a)//int(b)))
        elif intrinsic == "DROP":
            op_asm +=  '  add rsp, 8\n'
            try:
                STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot drop value from empty stack.")
        elif intrinsic == "DUP":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  push rax\n'
            op_asm +=  '  push rax\n'
            try:
                top = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Cannot duplicate value from empty stack.")
            STACK.append(top)
            STACK.append(top)
        elif intrinsic == "EXIT":
            op_asm +=  '  mov rax, 60\n'
            op_asm +=  '  mov rdi, 0\n'
            op_asm +=  '  syscall\n'
        elif intrinsic == "EQ":
            op_asm += get_comparison_asm("cmove")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a==b)))
        elif intrinsic == "GE":
            op_asm += get_comparison_asm("cmovge")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a>=b)))
        elif intrinsic == "GT":
            op_asm += get_comparison_asm("cmovg")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a>b)))
        elif intrinsic == "LE":
            op_asm += get_comparison_asm("cmovle")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a<=b)))
        elif intrinsic == "LT":
            op_asm += get_comparison_asm("cmovl")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a<b)))
        elif intrinsic == "MINUS":
            op_asm += get_arithmetic_asm("sub")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a) - int(b)))
        elif intrinsic == "MOD":
            op_asm +=  '  xor edx, edx ; Do not use floating point arithmetic\n'
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  div rbx\n'
            op_asm +=  '  push rdx ; Remainder\n'
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            STACK.append(str(int(a) % int(b)))
        elif intrinsic == "MUL":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  mul rbx\n'
            op_asm +=  '  push rax\n'
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            STACK.append(str(int(a) * int(b)))
        elif intrinsic == "NE":
            op_asm += get_comparison_asm("cmovne")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a!=b)))
        elif intrinsic == "OVER":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  push rbx\n'
            op_asm +=  '  push rax\n'
            op_asm +=  '  push rbx\n'
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
        elif intrinsic == "PLUS":
            op_asm += get_arithmetic_asm("add")
            try:
                b = STACK.pop()
                a = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            check_popped_value_type(op, a, expected_type='INT')
            check_popped_value_type(op, b, expected_type='INT')
            STACK.append(str(int(a) + int(b)))
        elif intrinsic == "PRINT":
            op_asm +=  '  pop rsi    ; *buf\n'
            op_asm +=  '  pop rdx    ; count\n'
            op_asm +=  '  mov rax, sys_write\n'
            op_asm +=  '  mov rdi, stdout\n'
            op_asm +=  '  syscall\n'
            try:
                buf = STACK.pop()
                count = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", \
                    f"Not enough values in the stack for syscall 'write'.\n{intrinsic} operand requires two values, *buf and count.")

            check_popped_value_type(op, buf, expected_type='*buf')
            check_popped_value_type(op, count, expected_type='INT')
        elif intrinsic == "PRINT_INT":
            op_asm +=  '  mov [int], rsi\n'
            op_asm +=  '  call PrintInt\n'
            op_asm +=  '  add rsp, 8\n'
            try:
                value = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Stack is empty")
            check_popped_value_type(op, value, expected_type='INT')
        elif intrinsic == "ROT":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  pop rcx\n'
            op_asm +=  '  push rbx\n'
            op_asm +=  '  push rax\n'
            op_asm +=  '  push rcx\n'
            try:
                a = STACK.pop()
                b = STACK.pop()
                c = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "The stack does not contain at least three elements to rotate.")
            STACK.append(b)
            STACK.append(a)
            STACK.append(c)
        elif intrinsic == "SWAP":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  push rax\n'
            op_asm +=  '  push rbx\n'
            try:
                a = STACK.pop()
                b = STACK.pop()
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
            STACK.append(a)
            STACK.append(b)
        elif intrinsic == "SWAP2":
            op_asm +=  '  pop rax\n'
            op_asm +=  '  pop rbx\n'
            op_asm +=  '  pop rcx\n'
            op_asm +=  '  pop rdx\n'
            op_asm +=  '  push rbx\n'
            op_asm +=  '  push rax\n'
            op_asm +=  '  push rdx\n'
            op_asm +=  '  push rcx\n'
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
        elif intrinsic == "SYSCALL0":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 0)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL1":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 1)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL2":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  pop rsi ; 2. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 2)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL3":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  pop rsi ; 2. arg\n"
            op_asm += "  pop rdx ; 3. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 3)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL4":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  pop rsi ; 2. arg\n"
            op_asm += "  pop rdx ; 3. arg\n"
            op_asm += "  pop r10 ; 4. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 4)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL5":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  pop rsi ; 2. arg\n"
            op_asm += "  pop rdx ; 3. arg\n"
            op_asm += "  pop r10 ; 4. arg\n"
            op_asm += "  pop r8  ; 5. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
            try:
                STACK = get_stack_after_syscall(STACK, 5)
            except IndexError:
                compiler_error(op, "POP_FROM_EMPTY_STACK", "Not enough values in the stack.")
        elif intrinsic == "SYSCALL6":
            op_asm += "  pop rax ; syscall\n"
            op_asm += "  pop rdi ; 1. arg\n"
            op_asm += "  pop rsi ; 2. arg\n"
            op_asm += "  pop rdx ; 3. arg\n"
            op_asm += "  pop r10 ; 4. arg\n"
            op_asm += "  pop r8  ; 5. arg\n"
            op_asm += "  pop r9  ; 6. arg\n"
            op_asm += "  syscall\n"
            op_asm += "  push rax ; return code\n"
    
    return op_asm

def get_op_size(op: Op, program: Program):
    COMPARISON_INSTRUCTIONS = ['cmove', 'cmovge', 'cmovg', 'cmovle', 'cmovl', 'cmovne']
    # http://unixwiz.net/techtips/x86-jumps.html
    JUMP_INSTRUCTIONS = ['jo', 'jno', 'js', 'jns', 'je', 'jz', 'jne', 'jnz', 'jb', 'jnae', 'jc', 'jnb', 'jae', 'jnc' \
        'jbe', 'jna', 'ja', 'jnbe', 'jl', 'jnge', 'jge', 'jng', 'jg', 'jnle', 'jp', 'jpe', 'jnp', 'jpo', 'jcxz', 'jecxz']
    REGISTERS = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp', 'rip', 'r8', 'r9', '10', 'r11', 'r12', 'r13', 'r14', 'r15']

    asm_instructions = get_op_asm(op, program).split('\n')[:-1]
    op_size = 0
    for row in asm_instructions:
        instruction = row.strip().split(' ')[0]
        if instruction in COMPARISON_INSTRUCTIONS:
            op_size += 4
        elif instruction in JUMP_INSTRUCTIONS:
            op_size += 6
        elif instruction == "call":
            op_size += 5
        elif instruction == "cmp":
            op_size += 3
        elif instruction == "mov":
            print(row)
            if re.match(r"\[\w+\]", row):
                print("JeEEE")
            op_size += 5
        elif instruction == "pop":
            op_size += 1
        elif instruction == "push":
            op_size += 1
        elif instruction =="syscall":
            op_size += 2
        elif instruction == "test":
            op_size += 3

    return op_size

def generate_asm(program: Program, asm_file: str) -> None:
    for op in program:
        token = op.token

        if op.type == OpType.PUSH_STR:
            str_val = token.value[1:-1]  # Take quotes out of the string
            add_string_variable_asm(asm_file, str_val, op)

        with open(asm_file, 'a') as f:
            f.write(get_op_comment_asm(op, op.type))
            op_asm = get_op_asm(op, program=program)
            if op_asm != "":
                f.write(op_asm)

    with open(asm_file, 'a') as f:
        f.write( ';; -- exit syscall\n')
        f.write( '  mov rax, sys_exit\n')
        f.write( '  mov rdi, success\n')
        f.write( '  syscall\n')
        f.close()

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{obj_file.replace(".o", "")}', obj_file])