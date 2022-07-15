#!/usr/bin/env python3
"""
Driver code for the Torth compiler
"""
import argparse
import os
from typing import List, Set
from compiler.compile import compile_code, link_object_file, remove_compilation_files
from compiler.defs import Constant, Function, Memory, Program, Token
from compiler.lex import add_enums_to_constants, get_constants_from_functions, get_functions_from_files
from compiler.lex import get_included_files, get_memories_from_code, get_tokens_from_functions
from compiler.utils import get_command_line_arguments, get_file_contents, handle_arguments
from compiler.utils import print_if_verbose

def main():
    """Program starts here"""
    args: argparse.Namespace    = get_command_line_arguments()
    print_if_verbose(f"Parsing the code from {args.code_file}", args.verbose)
    code: str                   = get_file_contents(args.code_file)
    compiler_directory: str     = os.path.dirname(os.path.abspath(__file__))
    included_files: Set[str]    = get_included_files(code, compiler_directory, args.path)
    included_files.add(args.code_file)

    functions: List[Function]   = get_functions_from_files(included_files)
    constants: List[Constant]   = get_constants_from_functions(functions)
    constants                   = add_enums_to_constants(included_files, constants)
    memories: List[Memory]      = get_memories_from_code(included_files, constants)
    code_file_basename: str     = os.path.basename(args.code_file)

    # Get all tokens in the order of execution
    tokens: List[Token] = get_tokens_from_functions(functions, code_file_basename)

    # Compile code into object file
    program: Program = compile_code(code_file_basename, tokens, constants, functions, memories, args.verbose)

    # Link the object file to a binary and remove compilation files
    executable_file: str = args.out or code_file_basename.replace('.torth', '.bin')
    object_file: str = code_file_basename.replace('.torth', '.o')
    print_if_verbose(f"Linking {object_file} to executable file {executable_file} with LD", args.verbose)
    link_object_file(object_file, executable_file, args)

    print_if_verbose("Removing files generated during compilation", args.verbose)
    remove_compilation_files(code_file_basename, args)

    # Handle special arguments --graph and --run
    handle_arguments(code_file_basename, executable_file, program, args)

if __name__ == "__main__":
    main()
