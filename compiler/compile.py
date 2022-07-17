"""
Functions required for compiling a Torth program
"""
import argparse
import subprocess
from typing import Dict, List
from compiler.asm import generate_asm
from compiler.defs import Constant, Memory, Program
from compiler.utils import print_if_verbose

def compile_asm(asm_file: str, object_file: str) -> None:
    """Compile the generated assembly source code with NASM."""
    subprocess.run(['nasm', '-felf64', f'-o{object_file}', asm_file], check=True)

def link_object_file(object_file: str, executable_file: str) -> None:
    """Link the compiled object file with LD."""
    subprocess.run(['ld', '-m', 'elf_x86_64', f'-o{executable_file}', object_file], check=True)

def compile_code(input_file: str, constants: List[Constant], \
    sub_programs: Dict[str, Program], memories: List[Memory], is_verbose: bool) -> None:
    """Generate assembly and compile it to statically linked ELF 64-bit executable."""
    # Generate assembly from Program
    assembly: str = generate_asm(sub_programs, constants, memories, is_verbose)

    # Write assembly to a file
    asm_file: str = input_file.replace('.torth', '.asm')
    with open(asm_file, 'w', encoding='utf-8') as f:
        f.write(assembly)

    # Compile the assembly code with NASM
    object_file: str = asm_file.replace(".asm", ".o")
    print_if_verbose(f"Compiling {asm_file} to {object_file} with NASM", is_verbose)
    compile_asm(asm_file, object_file)

def remove_compilation_files(input_file: str, args: argparse.Namespace) -> None:
    """Clean the current directory from compilation files."""
    input_file_extensionless: str = input_file.split('.')[0]
    subprocess.run(['rm', '-f', f'{input_file_extensionless}.o'], check=True)
    if not args.save_asm:
        subprocess.run(['rm', '-f', f'{input_file_extensionless}.asm'], check=True)
