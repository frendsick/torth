import argparse
import os
import sys

def usage() -> None:
    print("Usage: ./torth.py file")
    exit(1)

def get_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=f'{sys.argv[0]} [options] code_file', description='Compile Torth code')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--run', '-r', action='store_true', help='Run program after compilation')
    parser.add_argument('--save-asm', action='store_true', help='Save assembly file as <code_file>.asm')
    parser.add_argument('code_file', help='Input file')

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    if not os.path.isfile(args.code_file):
        FileNotFoundError(f"Argument '{sys.argv[1]}' is not a file")
    return args