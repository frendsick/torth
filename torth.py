#!/usr/bin/env python3
import argparse, os
from typing import List
from utils.defs import Token
from utils.lex import get_tokens_from_code
from utils.program import compile_code, remove_compilation_files, run_code
from utils.util import get_command_line_arguments

def main():
    args: argparse.Namespace = get_command_line_arguments()
    tokens: List[Token] = get_tokens_from_code(args.code_file)
    code_file_basename: str = os.path.basename(args.code_file)

    if args.output is not None:
        exe_file: str = args.output
    else:
        exe_file: str = code_file_basename.replace('.torth', '')

    compile_code(tokens, code_file_basename, exe_file)
    remove_compilation_files(code_file_basename, args)
    if args.run:
        run_code(exe_file)

if __name__ == "__main__":
    main()