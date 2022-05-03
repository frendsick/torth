import argparse
import os
import re
import sys
from typing import NoReturn, Optional
from compiler.defs import Colors, REGEX, Op

def usage() -> None:
    print("Usage: ./torth.py file")
    exit(1)

def get_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compile Torth code')
    parser.add_argument('--output', '-o', help='Output file', metavar='file')
    parser.add_argument('-r', '--run', action='store_true', help='Run program after compilation')
    parser.add_argument('-s', '--save-asm', action='store_true', help='Save assembly file as <code_file>.asm')
    parser.add_argument('code_file', help='Input file')

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    if not os.path.isfile(args.code_file):
        raise FileNotFoundError(f"Argument '{args.code_file}' is not a file")
    return args

def get_file_contents(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()

def compiler_error(op: Op, error_type: str, error_message: str) -> NoReturn:
    operand: str    = op.token.value
    file: str       = op.token.location[0]
    row: int        = op.token.location[1]
    col: int        = op.token.location[2]

    print(f'{Colors.HEADER}Compiler error {Colors.FAIL}{error_type}{Colors.NC}' + f":\n{error_message}\n")

    print(f'{Colors.HEADER}Operand{Colors.NC}: {operand}')
    print(f'{Colors.HEADER}File{Colors.NC}: {file}')
    print(f'{Colors.HEADER}Row{Colors.NC}: {row}, ' \
        + f'{Colors.HEADER}Column{Colors.NC}: {col}')
    exit(1)

def check_popped_value_type(op: Op, popped_value: str, expected_type: str) -> None:
    regex: str = REGEX[expected_type]
    error_message: str = f"Wrong type of value popped from the stack.\n\n" + \
        f"{Colors.HEADER}Value{Colors.NC}: {popped_value}\n" + \
        f"{Colors.HEADER}Expected{Colors.NC}: {expected_type}\n" + \
        f"{Colors.HEADER}Regex{Colors.NC}: {regex}"

    # Raise compiler error if the value gotten from the stack does not match with the regex
    assert re.match(regex, popped_value), compiler_error(op, "REGISTER_VALUE_ERROR", error_message)
