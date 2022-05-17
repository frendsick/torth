"""Utility functions for Torth compiler"""
import argparse
import os
import re
import sys
from typing import NoReturn, Optional
from compiler.defs import COLORS, Token, TYPE_REGEX

def usage() -> NoReturn:
    """Print usage message and exit with non-zero exit code"""
    print("Usage: ./torth.py file")
    sys.exit(1)

def get_command_line_arguments() -> argparse.Namespace:
    """Initialize ArgumendParser with command-line arguments and return the parser's Namespace"""
    parser = argparse.ArgumentParser(description='Compile Torth code')
    parser.add_argument('--output', '-o', help='Output file', metavar='file')
    parser.add_argument('-r', '--run', action='store_true', \
        help='Run program after compilation')
    parser.add_argument('-s', '--save-asm', action='store_true', \
        help='Save assembly file as <code_file>.asm')
    parser.add_argument('code_file', help='Input file')

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    if not os.path.isfile(args.code_file):
        compiler_error("ARGUMENT_ERROR", f"Argument '{args.code_file}' is not a file")
    return args

def get_file_contents(file_name: str) -> str:
    """Open a file in read-only mode and return the contents"""
    with open(file_name, 'r', encoding='utf8') as f:
        return f.read()

def compiler_error(error_type: str, error_message: str, token: Optional[Token] = None) -> NoReturn:
    """Output compiler error message to the console and exit with non-zero exit code"""
    print(f"{COLORS['HEADER']}Compiler error {COLORS['FAIL']}{error_type}{COLORS['NC']}" \
        + f":\n{error_message}")
    if token:
        print(get_token_location_info(token))
    sys.exit(1)

def get_token_location_info(token: Token) -> str:
    """Returns a string containing Token object's location in the source code"""
    return f'''
{COLORS['HEADER']}Operand{COLORS['NC']}: {token.value}
{COLORS['HEADER']}File{COLORS['NC']}: {token.location[0]}
{COLORS['HEADER']}Row{COLORS['NC']}: {token.location[1]}
{COLORS['HEADER']}Column{COLORS['NC']}: {token.location[2]}'''

def check_popped_value_type(token: Token, popped_value: str, expected_type: str) -> None:
    """Raises compiler error if the Token object is not of the required data type"""
    regex: str = TYPE_REGEX[expected_type]
    error_message: str = "Wrong type of value popped from the stack.\n\n" + \
        f"{COLORS['HEADER']}Value{COLORS['NC']}: {popped_value}\n" + \
        f"{COLORS['HEADER']}Expected{COLORS['NC']}: {expected_type}\n" + \
        f"{COLORS['HEADER']}Regex{COLORS['NC']}: {regex}"

    # Raise compiler error if the value gotten from the stack does not match with the regex
    assert re.match(regex, popped_value), \
        compiler_error("REGISTER_VALUE_ERROR", error_message, token)
