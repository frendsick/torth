#!/usr/bin/env python3
"""
Driver code for the Torth compiler
"""
import argparse
import os
from typing import List
from compiler.compile import compile_code, remove_compilation_files
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

    # Executable's file name is code file name without extension by default
    code_file_basename: str = os.path.basename(args.code_file)
    exe_file: str = args.output if args.output is not None \
        else code_file_basename.replace('.torth', '.bin')

    # Get all tokens in the order of execution
    tokens: List[Token] = get_tokens_from_functions(functions, code_file_basename)
    program: Program = compile_code(code_file_basename, exe_file, tokens, constants, memories)
    remove_compilation_files(code_file_basename, args)

    handle_arguments(args, exe_file, program)

if __name__ == "__main__":
    main()
