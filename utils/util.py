import sys
import os

def usage() -> None:
    print("Usage: ./torth.py file")
    exit(1)

def get_code_file_from_arguments() -> str:
    if len(sys.argv) != 2:
        usage()
    if os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    raise FileNotFoundError(f"Argument '{sys.argv[1]}' is not a file")