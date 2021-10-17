#!/usr/bin/env python3
from utils.lex import get_tokens_from_code
from utils.program import compile_code, run_code
from utils.util import get_code_file_from_arguments, usage

def main():
    code_file = get_code_file_from_arguments()
    tokens = get_tokens_from_code(code_file)
    compile_code(tokens)
    run_code(code_file.replace(".torth", ""))

if __name__ == "__main__":
    main()