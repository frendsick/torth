import subprocess
import sys
from typing import List
from utils.defs import Colors, OpType, Op, TokenType, Token, Program, STACK

# How many different string variables are stored to the program
STRING_COUNT = 0

def get_asm_file_start(asm_file:str) -> str:
    return '''default rel
extern printf

section .rodata
'''

def initialize_asm(asm_file: str) -> None:
    default_asm = get_asm_file_start(asm_file) + '''  formatStrInt db "%d",10,0

section .bss
  int: RESQ 1 ; allocates 8 bytes

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
def generate_comparison_asm(asm_file, cmov_operand: str) -> None:
    asm_file.write( '  pop rax\n')
    asm_file.write( '  pop rbx\n')
    asm_file.write( '  mov rcx, 0\n')
    asm_file.write( '  mov rdx, 1\n')
    asm_file.write( '  cmp rax, rbx\n')
    asm_file.write(f'  {cmov_operand} rcx, rdx\n')
    asm_file.write( '  push rcx\n')

def generate_arithmetic_asm(asm_file, operand: str) -> None:
    asm_file.write( '  pop rax\n')
    asm_file.write( '  pop rbx\n')
    asm_file.write(f'  {operand} rax, rbx\n')
    asm_file.write( '  push rax\n')

def add_string_variable_asm(asm_file: str, string: str) -> None:
    global STRING_COUNT
    STRING_COUNT += 1
    with open(asm_file, 'r') as f:
        file_lines = f.readlines()
    with open(asm_file, 'w') as f:
        f.write(get_asm_file_start(asm_file))
        f.write(f'  str{STRING_COUNT} db "{string}",10\n')
        f.write(f'  lenStr{STRING_COUNT} equ $-str{STRING_COUNT}\n\n')

        # Rewrite lines except for the first line (section .rodata)
        for i in range(4, len(file_lines)):
            f.write(file_lines[i])

def get_stack_after_syscall(stack: List[Token], param_count: int) -> List[Token]:
    syscall = stack.pop()
    for _i in range(param_count):
        stack.pop()
    syscall.value = '0' # Syscall return value is 0 by default
    stack.append(syscall)
    return stack

def compiler_error(op: Op, error_message: str) -> str:
    operand = op.token.value
    file    = op.token.location[0]
    row     = op.token.location[1]
    col     = op.token.location[2]
    print(Colors.FAIL + "Compiler error" + Colors.NC + f": {error_message}\n")

    print(Colors.HEADER + "Operand" + Colors.NC + f": {operand}")
    print(Colors.HEADER + "File" + Colors.NC + f": {file}")
    print(Colors.HEADER + "Row" + Colors.NC + f": {row}, " \
        + Colors.HEADER + "Column" + Colors.NC + f": {col}")
    exit(1)

def generate_asm(program: Program, asm_file: str) -> None:
    global STACK
    for op in program:
        token = op.token
        f = open(asm_file, 'a')
        # IF is just a keyword which does nothing
        if op.type == OpType.IF:
            f.write(get_op_comment_asm(op, op.type))
        elif op.type == OpType.PUSH_INT:
            f.write(get_op_comment_asm(op, op.type))
            f.write(f'  mov rax, {token.value}\n')
            f.write(f'  push rax\n')
            STACK.append(token)
        elif op.type == OpType.PUSH_STR:
            str_val = token.value[1:-1]  # Take quotes out of the string

            # Close the assembly file so the file can be rewritten in add_string_variable_asm
            f.close()
            add_string_variable_asm(asm_file, str_val)

            f = open(asm_file, 'a')
            f.write(get_op_comment_asm(op, op.type))
            f.write(f'  mov rsi, str{STRING_COUNT} ; Pointer to string\n')
            f.write( '  push rsi\n')
            STACK.append(token)
        elif op.type == OpType.INTRINSIC:
            intrinsic = token.value.upper()
            # Push argument count to the stack
            if intrinsic == "ARGC":
                f.write(get_op_comment_asm(op, op.type))
                f.write(f'  push {len(sys.argv)}\n')
                STACK.append(token)
            # Pop one element off the stack
            elif intrinsic == "DROP":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  add rsp, 8\n')
                try:
                    STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
            # Duplicate the top element of the stack
            elif intrinsic == "DUP":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  push rax\n')
                f.write( '  push rax\n')
                try:
                    top = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(top)
                STACK.append(top)
            elif intrinsic == "EQ":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmove")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a==b),TokenType.BOOL, token.location))
            elif intrinsic == "GE":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmovge")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a>=b),TokenType.BOOL, token.location))
            elif intrinsic == "GT":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmovgt")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a>b),TokenType.BOOL, token.location))
            elif intrinsic == "LE":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmovle")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a<=b),TokenType.BOOL, token.location))
            elif intrinsic == "LT":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmovl")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a<b),TokenType.BOOL, token.location))
            elif intrinsic == "NE":
                f.write(get_op_comment_asm(op, op.type))
                generate_comparison_asm(f, "cmovne")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(a!=b),TokenType.BOOL, token.location))
            elif intrinsic == "OVER":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  push rbx\n')
                f.write( '  push rax\n')
                f.write( '  push rbx\n')
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(a)
                STACK.append(b)
                STACK.append(a)
            elif intrinsic == "PLUS":
                f.write(get_op_comment_asm(op, op.type))
                generate_arithmetic_asm(f, "add")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(int(a.value)+int(b.value)),TokenType.INT, token.location))
            elif intrinsic == "MINUS":
                f.write(get_op_comment_asm(op, op.type))
                generate_arithmetic_asm(f, "sub")
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(int(a.value)-int(b.value)),TokenType.INT, token.location))
            elif intrinsic == "MUL":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  mul rbx\n')
                f.write( '  push rax\n')
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(int(a.value)*int(b.value)),TokenType.INT, token.location))
            # Rotate three top elements in the stack
            elif intrinsic == "ROT":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  pop rcx\n')
                f.write( '  push rbx\n')
                f.write( '  push rax\n')
                f.write( '  push rcx\n')
            # Push remainder and quotient to stack
            elif intrinsic == "DIVMOD":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  xor rdx, rdx\n')
                f.write( '  div rbx\n')
                f.write( '  push rdx ; Remainder\n')
                f.write( '  push rax ; Quotient\n')
                try:
                    b = STACK.pop()
                    a = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(Token(str(int(a.value)% int(b.value)),TokenType.INT, token.location))
                STACK.append(Token(str(int(a.value)//int(b.value)),TokenType.INT, token.location))
            elif intrinsic == "PRINT":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  mov rax, 1 ; write syscall\n')
                f.write( '  mov rdi, 1 ; fd 1 => stdout\n')
                f.write( '  mov rsi, [rsp] ; *buf\n')
                f.write(f'  mov rdx, lenStr{STRING_COUNT} ; count\n')
                f.write( '  syscall\n')
                f.write( '  add rsp, 8 ; drop str pointer from the stack\n')
                try:
                    STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
            # TODO: Reimplement PRINT_INT without using C-function printf
            elif intrinsic == "PRINT_INT":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  mov [int], rsi\n')
                f.write( '  call PrintInt\n')
                f.write( '  add rsp, 8\n')
                try:
                    STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
            # Swap two elements at the top of the stack
            elif intrinsic == "SWAP":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  push rax\n')
                f.write( '  push rbx\n')
                try:
                    a = STACK.pop()
                    b = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(a)
                STACK.append(b)
            # Swap two element pairs at the top of the stack
            elif intrinsic == "SWAP2":
                f.write(get_op_comment_asm(op, op.type))
                f.write( '  pop rax\n')
                f.write( '  pop rbx\n')
                f.write( '  pop rcx\n')
                f.write( '  pop rdx\n')
                f.write( '  push rbx\n')
                f.write( '  push rax\n')
                f.write( '  push rdx\n')
                f.write( '  push rcx\n')
                try:
                    a = STACK.pop()
                    b = STACK.pop()
                    c = STACK.pop()
                    d = STACK.pop()
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack.")
                STACK.append(b)
                STACK.append(a)
                STACK.append(d)
                STACK.append(c)
            elif intrinsic == "SYSCALL0":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 0)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL1":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 1)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL2":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  pop rsi ; 2. arg\n")
                f.write("  syscall\n");
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 2)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL3":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  pop rsi ; 2. arg\n")
                f.write("  pop rdx ; 3. arg\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 3)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL4":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  pop rsi ; 2. arg\n")
                f.write("  pop rdx ; 3. arg\n")
                f.write("  pop r10 ; 4. arg\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 4)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL5":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  pop rsi ; 2. arg\n")
                f.write("  pop rdx ; 3. arg\n")
                f.write("  pop r10 ; 4. arg\n")
                f.write("  pop r8  ; 5. arg\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 5)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            elif intrinsic == "SYSCALL6":
                f.write(get_op_comment_asm(op, op.type))
                f.write("  pop rax ; syscall\n")
                f.write("  pop rdi ; 1. arg\n")
                f.write("  pop rsi ; 2. arg\n")
                f.write("  pop rdx ; 3. arg\n")
                f.write("  pop r10 ; 4. arg\n")
                f.write("  pop r8  ; 5. arg\n")
                f.write("  pop r9  ; 6. arg\n")
                f.write("  syscall\n")
                f.write("  push rax ; return code\n")
                try:
                    STACK = get_stack_after_syscall(STACK, 6)
                except IndexError:
                    compiler_error(op, f"Not enough values in the stack")
            else:
                raise NotImplementedError(f"Intrinsic '{token.value}' is not implemented")
        else:
            raise NotImplementedError(f"Operand '{op.type}' is not implemented")
        
        for item in STACK:
            print(item.value, end=',')
        print()

    # Add exit syscall to asm_file
    f.write( ';; -- exit syscall\n')
    f.write( '  mov rax, 60\n')
    f.write( '  mov rdi, 0\n')
    f.write( '  syscall\n')
    f.close()

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{obj_file.replace(".o", "")}', obj_file])