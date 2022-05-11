import argparse
import os
import re
import sys
from typing import NoReturn, Optional
from compiler.defs import Colors, Op, Token, TYPE_REGEX

def usage() -> NoReturn:
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
        compiler_error("ARGUMENT_ERROR", f"Argument '{args.code_file}' is not a file")
    return args

def get_file_contents(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()

def compiler_error(error_type: str, error_message: str, token: Optional[Token] = None) -> NoReturn:
    print(f'{Colors.HEADER}Compiler error {Colors.FAIL}{error_type}{Colors.NC}' + f":\n{error_message}")
    if token:
        print(get_token_location_info(token))
    exit(1)

def get_token_location_info(token: Token) -> str:
    return f'''
{Colors.HEADER}Operand{Colors.NC}: {token.value}
{Colors.HEADER}File{Colors.NC}: {token.location[0]}
{Colors.HEADER}Row{Colors.NC}: {token.location[1]}
{Colors.HEADER}Column{Colors.NC}: {token.location[2]}'''

def check_popped_value_type(token: Token, popped_value: str, expected_type: str) -> None:
    regex: str = TYPE_REGEX[expected_type]
    error_message: str = f"Wrong type of value popped from the stack.\n\n" + \
        f"{Colors.HEADER}Value{Colors.NC}: {popped_value}\n" + \
        f"{Colors.HEADER}Expected{Colors.NC}: {expected_type}\n" + \
        f"{Colors.HEADER}Regex{Colors.NC}: {regex}"

    # Raise compiler error if the value gotten from the stack does not match with the regex
    assert re.match(regex, popped_value), compiler_error("REGISTER_VALUE_ERROR", error_message, token)
