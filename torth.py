#!/usr/bin/env python3
import os
from utils.lex import get_tokens_from_code
from utils.program import compile_code, run_code
from utils.util import get_code_file_from_arguments, usage

def main():
    code_file = get_code_file_from_arguments()
    tokens = get_tokens_from_code(code_file)
    compile_code(tokens)

    exe_file = os.path.basename(code_file).replace('.torth', '')
    run_code(exe_file)

if __name__ == "__main__":
    main()