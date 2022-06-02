"""
Functions required for compiling a Torth program
"""
import argparse
import subprocess
from typing import List
from compiler.asm import clean_asm, generate_asm, initialize_asm
from compiler.defs import Constant, Function, Memory, Program, Token
from compiler.lex import get_tokens_from_functions
from compiler.program import generate_program, type_check_program

def compile_asm(asm_file: str) -> None:
    """Compile the generated assembly source code with NASM."""
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file], check=True)

def link_object_file(obj_file: str, output_file: str) -> None:
    """Link the compiled object file with LD."""
    subprocess.run(['ld', '-m', 'elf_x86_64', f'-o{output_file}', obj_file], check=True)

def compile_code(input_file: str, output_file_basename: str, \
    constants: List[Constant], functions: List[Function], memories: List[Memory]) -> None:
    """Generate assembly and compile it to statically linked ELF 64-bit executable."""
    # Get all tokens in the order of execution
    tokens: List[Token] = get_tokens_from_functions(functions, input_file)

    # Generate Program from tokens and type check it with virtual stack
    program: Program = generate_program(tokens, memories)

    type_check_program(program)

    # Generate assembly from Program
    asm_file: str = input_file.replace('.torth', '.asm')
    initialize_asm(asm_file, constants, memories)
    generate_asm(asm_file, constants, program)
    clean_asm(asm_file)  # Remove unused code from the assembly

    # Compile the assembly code with NASM and link it with LD
    compile_asm(asm_file)
    link_object_file(asm_file.replace('.asm', '.o'), f'{output_file_basename}.bin')

def remove_compilation_files(input_file: str, args: argparse.Namespace) -> None:
    """Clean the current directory from compilation files."""
    input_file_extensionless: str = input_file.split('.')[0]
    subprocess.run(['rm', '-f', f'{input_file_extensionless}.o'], check=True)
    if not args.save_asm:
        subprocess.run(['rm', '-f', f'{input_file_extensionless}.asm'], check=True)
