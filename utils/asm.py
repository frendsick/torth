import subprocess
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

def generate_asm(program: Program, asm_file: str) -> None:
    with open (asm_file, 'a') as f:
        for op in program:
            if op.type == OpType.PUSH_INT:
                f.write(get_op_comment_asm(op, op.type))
                f.write(f'  mov rax, {op.token.value}\n')
                f.write(f'  push rax\n')
            elif op.type == OpType.INTRINSIC:
                intrinsic = op.token.value.upper()
                if intrinsic == "PLUS":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  add rax, rbx\n')
                    f.write( '  push rax\n')
                elif intrinsic == "MINUS":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write( '  pop rax\n')
                    f.write( '  pop rbx\n')
                    f.write( '  sub rax, rbx\n')
                    f.write( '  push rax\n')
                elif intrinsic == "PRINT_INT":
                    f.write(get_op_comment_asm(op, op.type))
                    f.write(f'  mov rsi, {op.type.value}\n')
                    f.write( '  mov [int], rsi\n')
                    f.write( '  call PrintInt\n')
                else:
                    raise NotImplementedError(f"Intrinsic '{op.token.value}' is not implemented")
            else:
                raise NotImplementedError(f"Operand '{op.type}' is not implemented")

        # Add exit syscall to asm_file
        f.write( '; -- exit syscall\n')
        f.write( '  mov rax, 0x1\n')
        f.write( '  xor rbx, rbx\n')
        f.write( '  int 0x80\n')

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{obj_file.replace(".o", "")}', obj_file])