import re
import os
from typing import List
from compiler.defs import Keyword, TokenType, Location, Token

def get_tokens_from_code(file: str, code: str) -> List[Token]:
    tokens: List[Token] = []
    token_matches: List[re.Match[str]] = get_token_matches(code)

    # Newlines are used to determine when a comment ends and when new line starts
    newline_indexes: List[int]  = [nl.start() for nl in re.finditer('\n', code)]

    for match in token_matches:
        token = get_token_from_match(match, os.path.basename(file), newline_indexes)
        tokens.append(token)

    return tokens

# Returns all tokens with comments taken out
def get_token_matches(code: str) -> List[re.Match[str]]:
    TOKEN_REGEX: re.Pattern[str] = re.compile(r'''\[.*\]|".*?"|'.*?'|\S+''')
    matches: List[re.Match[str]] = list(re.finditer(TOKEN_REGEX, code))
    code_without_comments: str = re.sub(r'\s*\/\/.*', '', code)
    matches_without_comments: List[re.Match[str]] = list(re.finditer(TOKEN_REGEX, code_without_comments))

    # Take comments out of matches
    i: int = 0
    while i < len(matches):
        match: str                  = matches[i].group(0)
        match_without_comments: str = matches_without_comments[i].group(0)

        # If i >= size of matches_without_comments list then the rest is comments
        if i >= len(matches_without_comments) or match != match_without_comments:
            matches.pop(i)
            i -= 1
        i += 1
    return matches

# Constructs and returns a Token object from a regex match
def get_token_from_match(match: re.Match[str], file: str, newline_indexes: List[int]) -> Token:
    token_value     = get_token_value(match.group(0))
    token_type      = get_token_type(token_value)
    token_location  = get_token_location(file, match.start(), newline_indexes)
    return Token(token_value, token_type, token_location)

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
    keywords: List[str] = ['DO', 'ELIF', 'ELSE', 'END', 'ENDIF', 'FUNC', 'IF', 'INCLUDE', 'WHILE']
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
