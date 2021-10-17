import subprocess
import sys
from utils.defs import OpType, Op, Program
def initialize_asm(asm_file: str) -> None:
    default_asm = '''default rel
extern printf

section .rodata
  formatStrInt db "%d",10,0

section .bss
  int: RESQ 1 ; allocates 8 bytes

section .text
PrintInt:
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

def generate_asm(program: Program, asm_file: str) -> None:
    with open (asm_file, 'a') as f:
        for op in program:
            # IF is just a keyword which does nothing
            if op.type == OpType.IF:
                f.write(get_op_comment_asm(op, op.type))
            elif op.type == OpType.PUSH_INT:
                f.write(get_op_comment_asm(op, op.type))
                f.write(f'  mov rax, {op.token.value}\n')
                f.write(f'  push rax\n')
            elif op.type == OpType.INTRINSIC:
                intrinsic = op.token.value.upper()
                # Push argument count to the stack
                if intrinsic == "ARGC":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write(f'  push {len(sys.argv)}\n')
                # Pop one element off the stack
                elif intrinsic == "DROP":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                # Duplicate the top element of the stack
                elif intrinsic == "DUP":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  push rax\n')
                    f.write( '  push rax\n')
                elif intrinsic == "EQ":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmove")
                elif intrinsic == "GE":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmovge")
                elif intrinsic == "GT":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmovgt")
                elif intrinsic == "LE":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmovle")
                elif intrinsic == "LT":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmovl")
                elif intrinsic == "NE":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_comparison_asm(f, "cmovne")
                elif intrinsic == "OVER":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  push rbx\n')
                    f.write( '  push rax\n')
                    f.write( '  push rbx\n')
                elif intrinsic == "PLUS":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_arithmetic_asm(f, "add")
                elif intrinsic == "MINUS":
                    f.write(get_op_comment_asm(op, op.type))
                    generate_arithmetic_asm(f, "sub")
                elif intrinsic == "MUL":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  mul rbx\n')
                    f.write( '  push rax\n')
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
                elif intrinsic == "PRINT_INT":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  mov [int], rsi\n')
                    f.write( '  call PrintInt\n')
                # Swap two elements at the top of the stack
                elif intrinsic == "SWAP":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  push rax\n')
                    f.write( '  push rbx\n')
                elif intrinsic == "SYSCALL0":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL1":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  pop rdi\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL2":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n");
                    f.write("  pop rdi\n");
                    f.write("  pop rsi\n");
                    f.write("  syscall\n");
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL3":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  pop rdi\n")
                    f.write("  pop rsi\n")
                    f.write("  pop rdx\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL4":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  pop rdi\n")
                    f.write("  pop rsi\n")
                    f.write("  pop rdx\n")
                    f.write("  pop r10\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL5":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  pop rdi\n")
                    f.write("  pop rsi\n")
                    f.write("  pop rdx\n")
                    f.write("  pop r10\n")
                    f.write("  pop r8\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                elif intrinsic == "SYSCALL6":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write("  pop rax\n")
                    f.write("  pop rdi\n")
                    f.write("  pop rsi\n")
                    f.write("  pop rdx\n")
                    f.write("  pop r10\n")
                    f.write("  pop r8\n")
                    f.write("  pop r9\n")
                    f.write("  syscall\n")
                    f.write("  push rax\n")
                else:
                    raise NotImplementedError(f"Intrinsic '{op.token.value}' is not implemented")
            else:
                raise NotImplementedError(f"Operand '{op.type}' is not implemented")

        # Add exit syscall to asm_file
        f.write( ';; -- exit syscall\n')
        f.write( '  mov rax, 0x1\n')
        f.write( '  xor rbx, rbx\n')
        f.write( '  int 0x80\n')

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{obj_file.replace(".o", "")}', obj_file])