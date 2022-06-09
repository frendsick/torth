#!/usr/bin/env python3
"""
Driver code for the Torth compiler
"""
import argparse
import os
from typing import List
from compiler.compile import compile_code, link_object_file, remove_compilation_files
from compiler.defs import Constant, Function, Memory, Program, Token
from compiler.lex import get_constants_from_functions, get_functions_from_files
from compiler.lex import get_included_files, get_memories_from_code, get_tokens_from_functions
from compiler.utils import get_command_line_arguments, get_file_contents, handle_arguments

def main():
    """Program starts here"""
    args: argparse.Namespace    = get_command_line_arguments()
    code: str                   = get_file_contents(args.code_file)
    included_files: List[str]   = get_included_files(code)
    functions: List[Function]   = get_functions_from_files(args.code_file, included_files)
    constants: List[Constant]   = get_constants_from_functions(functions)
    memories: List[Memory]      = get_memories_from_code(included_files, constants)
    code_file_basename: str     = os.path.basename(args.code_file)

    # Get all tokens in the order of execution
    tokens: List[Token] = get_tokens_from_functions(functions, code_file_basename)

    # Compile code into object file
    program: Program = compile_code(code_file_basename, tokens, constants, functions, memories)

    # Link the object file to a binary and remove compilation files
    executable_file: str = args.out or code_file_basename.replace('.torth', '.bin')
    link_object_file(code_file_basename, executable_file, args)
    remove_compilation_files(code_file_basename, args)

    # Handle special arguments --graph and --run
    handle_arguments(code_file_basename, executable_file, program, args)

if __name__ == "__main__":
    main()
