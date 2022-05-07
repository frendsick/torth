import argparse
import subprocess
from typing import List
from compiler.asm import generate_asm, initialize_asm
from compiler.defs import Program, Token
from compiler.program import generate_program, type_check_program

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str, output_file: str) -> None:
    subprocess.run(['ld', '-m', 'elf_x86_64', f'-o{output_file}', obj_file])

def compile_code(tokens: List[Token], input_file: str, output_file: str) -> None:
    asm_file: str = input_file.replace('.torth', '.asm')
    program: Program = generate_program(tokens, input_file)
    type_check_program(program)
    initialize_asm(asm_file)
    generate_asm(program, asm_file)
    compile_asm(asm_file)
    link_object_file(asm_file.replace('.asm', '.o'), output_file)

def remove_compilation_files(input_file: str, args: argparse.Namespace) -> None:
    input_file_extensionless: str = input_file.split('.')[0]
    subprocess.run(['rm', '-f', f'{input_file_extensionless}.o'])
    if not args.save_asm:
        subprocess.run(['rm', '-f', f'{input_file_extensionless}.asm'])
