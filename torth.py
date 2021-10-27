#!/usr/bin/env python3
import os
from utils.lex import get_tokens_from_code
from utils.program import compile_code, remove_compilation_files, run_code
from utils.util import get_command_line_arguments

def main():
    args = get_command_line_arguments()
    tokens = get_tokens_from_code(args.code_file)
    code_file_basename = os.path.basename(args.code_file)

    if args.output is not None:
        exe_file = args.output
    else:
        exe_file = code_file_basename.replace('.torth', '')

    compile_code(tokens, code_file_basename, exe_file)
    remove_compilation_files(code_file_basename, args)
    if args.run:
        run_code(exe_file)

if __name__ == "__main__":
    main()