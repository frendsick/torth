"""
Functions required for compiling a Torth program
"""
import argparse
import subprocess
from typing import List
from compiler.asm import generate_asm, initialize_asm
from compiler.defs import Constant, Function, Memory, Program, Token
from compiler.program import generate_program, type_check_program
from compiler.utils import print_if_verbose

def compile_asm(asm_file: str, object_file: str) -> None:
    """Compile the generated assembly source code with NASM."""
    subprocess.run(['nasm', '-felf64', f'-o{object_file}', asm_file], check=True)

def link_object_file(object_file: str, executable_file: str, cmd_args) -> None:
    """Link the compiled object file with LD."""
    if cmd_args.debug:
        subprocess.run(['ld', '-m', 'elf_x86_64', f'-o{executable_file}', object_file], check=True)
    else:
        subprocess.run(['ld', '--strip-all', '-m', 'elf_x86_64', f'-o{executable_file}', object_file], check=True)

def compile_code(input_file: str, tokens: List[Token], constants: List[Constant], \
    functions: List[Function], memories: List[Memory], is_verbose: bool) -> Program:
    """Generate assembly and compile it to statically linked ELF 64-bit executable."""

    # Generate Program from tokens and type check it with virtual stack
    print_if_verbose("Generating intermediate representation from the parsed tokens", is_verbose)
    program: Program = generate_program(tokens, constants, functions, memories)

    # Type check the program
    print_if_verbose("Type checking the program", is_verbose)
    type_check_program(program)

    # Generate assembly from Program
    print_if_verbose("Generating Assembly from the intermediate representation", is_verbose)
    assembly: str = initialize_asm(constants, memories)
    assembly      = generate_asm(assembly, constants, program)

    # Write assembly to a file
    asm_file: str = input_file.replace('.torth', '.asm')
    with open(asm_file, 'w', encoding='utf-8') as f:
        f.write(assembly)

    # Compile the assembly code with NASM
    object_file: str = asm_file.replace(".asm", ".o")
    print_if_verbose(f"Compiling {asm_file} to {object_file} with NASM", is_verbose)
    compile_asm(asm_file, object_file)
    return program

def remove_compilation_files(input_file: str, args: argparse.Namespace) -> None:
    """Clean the current directory from compilation files."""
    input_file_extensionless: str = input_file.split('.')[0]
    subprocess.run(['rm', '-f', f'{input_file_extensionless}.o'], check=True)
    if not args.save_asm:
        subprocess.run(['rm', '-f', f'{input_file_extensionless}.asm'], check=True)
