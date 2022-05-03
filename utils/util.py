import argparse
import os
import sys

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
