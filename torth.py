#!/usr/bin/env python3
"""
Driver code for the Torth compiler
"""
import argparse
import os
from typing import Dict, List, Set
from compiler.compile import compile_code, link_object_file, remove_compilation_files
from compiler.defs import Constant, Function, Memory, Program
from compiler.program import get_sub_programs, type_check_program
from compiler.lex import (
    add_enums_to_constants,
    get_constants_from_files,
    get_functions_from_files,
    get_included_files,
    get_memories_from_code,
    parse_function_bindings,
)
from compiler.utils import (
    get_command_line_arguments,
    get_file_contents,
    handle_arguments,
    print_if_verbose,
)


def main():
    """Program starts here"""
    args: argparse.Namespace = get_command_line_arguments()
    print_if_verbose(f"Parsing the code from {args.code_file}", args.verbose)
    code: str = get_file_contents(args.code_file)
    compiler_directory: str = os.path.dirname(os.path.abspath(__file__))
    included_files: Set[str] = get_included_files(code, compiler_directory, args.path)
    included_files.add(args.code_file)

    functions: Dict[str, Function] = get_functions_from_files(included_files)
    constants: List[Constant] = get_constants_from_files(included_files)
    constants = add_enums_to_constants(included_files, constants)
    memories: List[Memory] = get_memories_from_code(included_files, constants)
    functions = parse_function_bindings(functions, memories)
    sub_programs: Dict[str, Program] = get_sub_programs(functions, constants, memories)
    code_file_basename: str = os.path.basename(args.code_file)

    # Type check sub-programs
    print_if_verbose("Type checking Functions", args.verbose)
    for function_name, program in sub_programs.items():
        type_check_program(functions[function_name], program, functions)

    # Compile code into object file
    compile_code(code_file_basename, constants, sub_programs, memories, args.verbose)

    # Link the object file to a binary and remove compilation files
    executable_file: str = args.out or code_file_basename.replace(".torth", ".bin")
    object_file: str = code_file_basename.replace(".torth", ".o")
    print_if_verbose(
        f"Linking {object_file} to executable file {executable_file} with LD",
        args.verbose,
    )
    link_object_file(object_file, executable_file)

    print_if_verbose("Removing files generated during compilation", args.verbose)
    remove_compilation_files(code_file_basename, args)

    # Handle special arguments --graph and --run
    handle_arguments(executable_file, args)


if __name__ == "__main__":
    main()
