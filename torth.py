#!/usr/bin/env python3
import argparse
import os
import re
from typing import List
from compiler.compile import compile_code, remove_compilation_files
from compiler.defs import Token
from compiler.lex import get_tokens_from_code
from compiler.program import run_code
from compiler.utils import get_command_line_arguments, get_file_contents

def main():
    args: argparse.Namespace = get_command_line_arguments()
    code: str = get_file_contents(args.code_file)
    code_file_basename: str = os.path.basename(args.code_file)
    tokens: List[Token] = get_tokens_from_code(code, code_file_basename)

    # Executable's file name is code file name without extension by default
    exe_file: str = args.output if args.output is not None else code_file_basename.replace('.torth', '')

    compile_code(tokens, code_file_basename, exe_file)
    remove_compilation_files(code_file_basename, args)
    if args.run:
        run_code(exe_file)

if __name__ == "__main__":
    main()