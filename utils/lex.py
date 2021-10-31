import re
import os
from typing import List
from utils.defs import INCLUDE_PATHS, Keyword, TokenType, Location, Token

# Returns the Intrinsic class value from token
def get_token_value(token: str) -> str:
    if token == '%':
        return 'MOD'
    if token == '/':
        return 'DIV'
    if token == '==':
        return 'EQ'
    if token == '>=':
        return 'GE'
    if token == '>':
        return 'GT'
    if token == '<=':
        return 'LE'
    if token == '<':
        return 'LT'
    if token == '-':
        return 'MINUS'
    if token == '*':
        return 'MUL'
    if token == '!=':
        return 'NE'
    if token == '+':
        return 'PLUS'
    if token == '.':
        return 'PRINT_INT'
    if token == 'TRUE':
        return '1'
    if token == 'FALSE':
        return '0'
    return token

def get_token_type(token_text: str) -> TokenType:
    keywords = ['DO', 'ELIF', 'ELSE', 'END', 'ENDIF', 'IF', 'INCLUDE', 'MACRO', 'WHILE']
    # Check if all keywords are taken into account
    assert len(Keyword) == len(keywords) , f"Wrong number of keywords in get_token_type function! Expected {len(Keyword)}, got {len(keywords)}"

    # Keywords are case insensitive
    if token_text.upper() in keywords:
        return TokenType.KEYWORD
    if re.search(r'ARRAY\(.+\)', token_text.upper()):
        return TokenType.ARRAY
    if token_text.upper() in ('TRUE', 'FALSE'):
        return TokenType.BOOL
    if token_text[0] == token_text[-1] == '"':
        return TokenType.STR
    if token_text[0] == token_text[-1] == "'":
        return TokenType.CSTR
    try:
        _integer = int(token_text)
        return TokenType.INT
    except ValueError:
        return TokenType.WORD

# Returns tuple containing the row and the column where the token was found
def get_token_location(filename: str, position: int, newline_indexes: List[int]) -> Location:
    col = position
    row = 1
    for i in range(len(newline_indexes)):
        if i > 0:
            col = position - newline_indexes[i-1] - 1
            row +=1
        if newline_indexes[i] > position:
            return (filename, row, col)
    
    if len(newline_indexes) >= 1:
        row += 1
        col = position - newline_indexes[-1] - 1
    return (filename, row, col)

def include_file_to_code(file: str, code: str, line: int) -> str:
    with open(file, 'r') as f:
        include_lines = f.read().splitlines()
    old_lines = code.splitlines()
    new_lines = old_lines[:line] + include_lines + old_lines[line+1:]
    return '\n'.join(new_lines)

def include_files(code: str) -> str:
    code_lines = code.splitlines()
    row  = 0
    rows = len(code_lines)
    for line in code_lines:
        match = re.search(r'^\s*include\s+(\S+)\s*$', line)
        if match:
            for path in INCLUDE_PATHS:
                include_file = path + match.group(1) + ".torth"
                if os.path.isfile(include_file):
                    code = include_file_to_code(include_file, code, row)
                    row += len(code.splitlines()) - rows
        row += 1
    return code

def get_macros(code: str) -> dict:
    code_lines      = code.splitlines()
    defined_macros  = {}
    for line in code_lines:
        match = re.search(r'\s*macro\s+(.+?)\s+(.+)\s+end', line)
        if match:
            defined_macros[match.group(1)] = match.group(2)
    return defined_macros

def get_tokens_from_macro(macro: str, defined_macros: dict) -> list:
    return [token for token in re.finditer(r'".*?"|\S+', defined_macros[macro])]

def get_tokens(code: str, defined_macros: dict) -> list:
    original_tokens     = [token for token in re.finditer(r'''\w+\(.+\)|".*?"|'.*?'|\S+''', code)]
    real_tokens         = []    # Tokens with macros interpreted
    for match in original_tokens:
        if match.group(0) in defined_macros:
            real_tokens += get_tokens_from_macro(match.group(0), defined_macros)
        else:
            real_tokens.append(match)
    return real_tokens

def get_tokens_from_code(code_file: str) -> List[Token]:
    with open(code_file, 'r') as f:
        code = f.read()
    
    # Remove all comments from the code
    code = re.sub(r'\s*\/\/.*', '', code)

    # Add included files to code and interpret defined macros
    code            = include_files(code)
    defined_macros  = get_macros(code)

    # Remove all macros from the code
    code = re.sub(r'\s*macro.+end\s*', '', code)
    token_matches = get_tokens(code, defined_macros)

    # Get all newline characters and tokens with their locations from the code
    newline_indexes = [i for i in range(len(code)) if code[i] == '\n']

    tokens = []
    for match in token_matches:
        value     = get_token_value(match.group(0))
        type      = get_token_type(value)
        location  = get_token_location(os.path.basename(code_file), match.start()+1, newline_indexes)
        token     = Token(value, type, location)
        tokens.append(token)

    return tokens
