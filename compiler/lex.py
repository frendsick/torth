import re
import os
from typing import List, Tuple
from compiler.defs import Keyword, TokenType, Location, Token

def get_tokens_from_code(file: str, code: str, macro_location: Location = None) -> List[Token]:
    MACRO_REGEX: re.Pattern[str]        = re.compile(r'\s*MACRO\s+(\S+)\s+(.*)\s+END\s*', re.IGNORECASE)
    token_matches: List[re.Match[str]]  = get_token_matches(code, MACRO_REGEX)

    # Newlines are used to determine when a comment ends and when new line starts
    newline_indexes: List[int]  = [nl.start() for nl in re.finditer('\n', code)]

    tokens: List[Token]             = []
    macros: List[Tuple[str,str]]    = re.findall(MACRO_REGEX, code)
    for match in token_matches:
        token = get_token_from_match(match, os.path.basename(file), newline_indexes, macros, macro_location)
        tokens.append(token)

    return tokens

# Returns all tokens with comments taken out
def get_token_matches(code: str, macro_regex: re.Pattern[str]) -> List[re.Match[str]]:
    TOKEN_REGEX: re.Pattern[str] = re.compile(r'''\[.*\]|".*?"|'.*?'|\S+''')

    matches: List[re.Match[str]]            = list(re.finditer(TOKEN_REGEX, code))
    code_without_comments: str              = re.sub(r'\s*\/\/.*', '', code)
    code_without_macros: str                = re.sub(macro_regex, '', code_without_comments)
    final_code_matches: List[re.Match[str]] = list(re.finditer(TOKEN_REGEX, code_without_macros))

    # Take comments and macros out of matches
    i: int = 0
    while i < len(matches):
        match: str = matches[i].group(0)

        # If i >= size of matches_without_comments list then the rest is comments
        if i >= len(final_code_matches) or match != final_code_matches[i].group(0):
            matches.pop(i)
            i -= 1
        i += 1
    return matches

def merge_macros_to_matches(macros: List[Tuple[str, str]], matches: List[re.Match[str]]) -> List[re.Match[str]]:
    for macro in macros:
        macro_name: str = macro[0]
        macro_code: str = macro[1]

        # Replace all references to macro's name with macro's content


def merge_macros_to_code(code: str, macro_regex: str) -> str:
    macros: List[Tuple[str, str]] = re.findall(macro_regex, code)
    for macro in macros:
        # Remove macros from code
        code = re.sub(macro_regex, '', code, count=1)

        # Replace all calls to the macro with the macro contents
        code = code.replace(macro[0], macro[1])
    return code

# Constructs and returns a Token object from a regex match
def get_token_from_match(match: re.Match[str], file: str, newline_indexes: List[int], macros: List[Tuple[str,str]], macro_location: Location) -> Token:
    token_value: str        = get_token_value(match.group(0), macros)
    token_type: TokenType   = get_token_type(token_value)
    token_location          = macro_location or get_token_location(file, match.start(), newline_indexes)
    return Token(token_value, token_type, token_location)

# Returns the Intrinsic class value from token
def get_token_value(token: str, macros: List[Tuple[str,str]]) -> str:
    token = token.upper()
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
    if token == '^':
        return 'POW'
    if token == '.':
        return 'PRINT_INT'
    if token == 'TRUE':
        return '1'
    if token == 'FALSE':
        return '0'
    for macro in macros:
        macro_name: str = macro[0].upper()
        if token == macro_name:
            return macro[1]  # Macro's code
    return token

def get_token_type(token_text: str) -> TokenType:
    keywords: List[str] = ['BREAK', 'DO', 'ELIF', 'ELSE', 'END', 'ENDIF', 'IF', 'MACRO', 'WHILE']
    # Check if all keywords are taken into account
    assert len(Keyword) == len(keywords) , f"Wrong number of keywords in get_token_type function! Expected {len(Keyword)}, got {len(keywords)}"

    # Keywords are case insensitive
    if token_text.upper() in keywords:
        return TokenType.KEYWORD
    if re.search(r'ARRAY\(.+\)', token_text.upper()):
        return TokenType.ARRAY
    if token_text.upper() in {'TRUE', 'FALSE'}:
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
    col: int = position
    row: int = 1
    for i in range(len(newline_indexes)):
        if i > 0:
            col = position - newline_indexes[i-1] - 1
            row +=1
        if newline_indexes[i] > position:
            return (filename, row, col+1)

    if newline_indexes:
        row += 1
        col = position - newline_indexes[-1] - 1
    return (filename, row, col+1)
