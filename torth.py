#!/usr/bin/env python3
import argparse
import os
from typing import List
from compiler.compile import compile_code, remove_compilation_files
from compiler.defs import Function, Token
from compiler.lex import get_functions_from_code, get_included_files, get_tokens_from_functions
from compiler.program import run_code
from compiler.utils import get_command_line_arguments, get_file_contents

def main():
    args: argparse.Namespace = get_command_line_arguments()
    code: str = get_file_contents(args.code_file)
    included_files: List[str]   = get_included_files(code)
    functions: List[Function]   = get_functions_from_code(code, args.code_file, included_files)

    # Executable's file name is code file name without extension by default
    code_file_basename: str = os.path.basename(args.code_file)
    exe_file: str = args.output if args.output is not None else code_file_basename.replace('.torth', '')

    compile_code(code_file_basename, exe_file, functions)
    remove_compilation_files(code_file_basename, args)
    if args.run:
        run_code(exe_file)

if __name__ == "__main__":
    main()