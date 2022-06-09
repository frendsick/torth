"""
Functions required for compiling a Torth program
"""
import argparse
import subprocess
from typing import List
from compiler.asm import clean_asm, generate_asm, initialize_asm
from compiler.defs import Constant, Function, Memory, Program, Token
from compiler.program import generate_program, type_check_program

def compile_asm(asm_file: str) -> None:
    """Compile the generated assembly source code with NASM."""
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file], check=True)

def link_object_file(input_file: str, executable_file: str, cmd_args) -> None:
    """Link the compiled object file with LD."""
    object_file: str = input_file.replace('.torth', '.o')
    if cmd_args.debug:
        subprocess.run(['ld', '-m', 'elf_x86_64', f'-o{executable_file}', object_file], check=True)
    else:
        subprocess.run(['ld', '--strip-all', '-m', 'elf_x86_64', f'-o{executable_file}', object_file], check=True)

def compile_code(input_file: str, tokens: List[Token], \
    constants: List[Constant], functions: List[Function], memories: List[Memory]) -> Program:
    """Generate assembly and compile it to statically linked ELF 64-bit executable."""

    # Generate Program from tokens and type check it with virtual stack
    program: Program = generate_program(tokens, functions, memories)

    # Type check the program
    type_check_program(program)

    # Generate assembly from Program
    assembly: str = initialize_asm(constants, memories)
    assembly      = generate_asm(assembly, constants, program)
    assembly      = clean_asm(assembly)  # Remove unused code from the assembly

    # Write assembly to a file
    asm_file: str = input_file.replace('.torth', '.asm')
    with open(asm_file, 'w', encoding='utf-8') as f:
        f.write(assembly)

    # Compile the assembly code with NASM
    compile_asm(asm_file)
    return program

def remove_compilation_files(input_file: str, args: argparse.Namespace) -> None:
    """Clean the current directory from compilation files."""
    input_file_extensionless: str = input_file.split('.')[0]
    subprocess.run(['rm', '-f', f'{input_file_extensionless}.o'], check=True)
    if not args.save_asm:
        subprocess.run(['rm', '-f', f'{input_file_extensionless}.asm'], check=True)
