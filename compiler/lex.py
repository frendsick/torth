"""
The module implements lexing functions that parses Tokens from code files
"""
import itertools
import re
from typing import List, Optional
from compiler.defs import Constant, Function, Keyword, Location, Memory
from compiler.defs import Signature, SIGNATURE_MAP, Token, TokenType
from compiler.utils import compiler_error, get_file_contents

def get_included_files(code: str):
    """Parse included files from a code string. Return the list of files."""
    INCLUDE_REGEX = re.compile(r'INCLUDE\s+"(\S+)"', flags=re.MULTILINE | re.IGNORECASE)
    included_files: List[str] = INCLUDE_REGEX.findall(code)
    for file in included_files:
        included_code: str = get_file_contents(file)
        included_files += get_included_files(included_code)
    return included_files

def get_functions_from_files(file_name: str, included_files: List[str]) -> List[Function]:
    """Parse declared functions from code file and included files. Return list of Function objects."""
    functions: List[Function] = []
    included_files.append(file_name)
    for file in included_files:
        included_code: str = get_file_contents(file)
        token_matches: list = get_token_matches(included_code)
        # Newlines are used to determine when a comment ends and when new line starts
        newline_indexes: List[int] = [nl.start() for nl in re.finditer('\n', included_code)]
        functions += get_functions(file, token_matches, newline_indexes)
    return functions

def get_tokens_from_functions(functions: List[Function], file: str) -> List[Token]:
    """
    Check if a main function is present in code file and parse Tokens from Functions.
    Raise a compiler error MISSING_MAIN_FUNCTION if main function is not present.
    Return a list of Token objects.
    """
    try:
        main_function: Function = [ func for func in functions if func.name.upper() == 'MAIN' ][0]
        if not main_function.tokens:
            return []
    except IndexError:
        compiler_error("MISSING_MAIN_FUNCTION", f"The program {file} does not have a main function")
    return get_tokens_from_function(main_function, functions)

def get_tokens_from_function(parent_function: Function, functions: List[Function]) -> List[Token]:
    """Parse Tokens from a single Function object. Return a list of Token objects."""
    tokens: List[Token] = parent_function.tokens
    i = 0
    while i < len(tokens):
        for func in functions:
            child_function: Optional[Function] = func if tokens[i].value == func.name else None
            if child_function:
                tokens = tokens[:i] + get_tokens_from_function(child_function, functions) + tokens[i+1:]
        i += 1
    return tokens

def get_functions(file: str, token_matches: list, newline_indexes: List[int]) -> List[Function]:
    """
    Parse Functions from a list containing re.Matches of tokens parsed from a code file.
    Return list of Function objects.
    """
    # Initialize variables
    functions: List[Function]       = []
    current_part: int               = 0
    name: str                       = ''
    param_types: List[TokenType]    = []
    return_types: List[TokenType]   = []
    tokens: List[Token]             = []

    # CONST is a constant integer so a function with Signature( [], ['INT'] )
    is_const: bool = False

    # Functions are made of four parts:
    #  1 : name,
    #  2 : param types
    #  3 : return types
    #  4 : location
    # (0 : Not lexing a function)
    FUNCTION_PART_DELIMITERS: List[str] = ['FUNCTION', '_name', '->', ':', 'END']
    function_parts = itertools.cycle(list(range(5)))
    next(function_parts)

    for match in token_matches:
        token_value: str = match.group(0)
        if token_value.upper() == 'CONST':
            is_const = True
            token_value = token_value.upper().replace('CONST', 'FUNCTION')

        # Go to next function part
        if token_value.upper() == FUNCTION_PART_DELIMITERS[current_part]:
            current_part = next(function_parts)

            # Append Function and reset variables when function is fully lexed
            if token_value.upper() == 'END':
                signature: Signature = (param_types, return_types)
                tokens.append(Token(f'FUNCTION_RETURN', TokenType.KEYWORD, tokens[-1].location))
                functions.append( Function(name, signature, tokens) )
                name            = ''
                param_types     = []
                return_types    = []
                tokens          = []
                is_const        = False

        elif current_part == 1:
            name = token_value
            if is_const:
                # CONST is a constant integer so a function with Signature( [], [TokenType.INT] )
                return_types.append(TokenType.INT)

                # Defining CONST skips -> and : delimiters
                next(function_parts)
                next(function_parts)
            current_part = next(function_parts)
        elif current_part == 2:
            param_types.append(SIGNATURE_MAP[token_value.upper()])
        elif current_part == 3:
            return_types.append(SIGNATURE_MAP[token_value.upper()])
        elif current_part == 4:
            token: Token = get_token_from_match(match, file, newline_indexes)
            if not tokens:
                tokens.append(Token(f'FUNCTION_CALL', TokenType.KEYWORD, token.location))
            tokens.append(token)
    return functions

def get_memories_from_code(included_files: List[str], constants: List[Constant]) -> List[Memory]:
    """Parse Memory objects from code file and included files. Return list of Memory objects."""
    memories: List[Memory] = []
    for file in included_files:
        included_code: str = get_file_contents(file)
        token_matches: list = get_token_matches(included_code)
        newline_indexes: List[int] = [nl.start() for nl in re.finditer('\n', included_code)]
        memories += get_memories(file, token_matches, newline_indexes, constants)
    return memories

def get_memories(file: str, token_matches: list, newline_indexes: List[int], constants: List[Constant]) -> List[Memory]:
    """Parse Memory objects from a single code file. Return list of Memory objects."""
    memories: List[Memory]  = []
    name: str               = ''
    size: str               = ''
    defining_memory: bool   = False
    for match in token_matches:
        token_value: str = match.group(0)
        if defining_memory:
            if not name:
                name = get_memory_name(token_value, memories)
                location: Location = get_token_location(file, match.start(), newline_indexes)
                continue

            if not size:
                size = get_memory_size(token_value, constants)
                memory: Memory = (name, size, location)
                memories.append(memory)
                defining_memory = False

                # Reset variables
                name = ''
                size = ''
                continue
        if token_value.upper() == 'MEMORY':
            defining_memory = True
    return memories

def get_memory_name(token_value: str, memories: List[Memory]) -> str:
    """Check for redefinition of a Memory object. Return list of Memory objects."""
    # Overwriting token name with memory is not allowed
    if token_value in memories:
        compiler_error("MEMORY_REDEFINITION", f"Memory '{token_value}' already exists. Memory name should be unique.")
    return token_value

def get_memory_size(token_value: str, constants: List[Constant]) -> str:
    """Verify if the size parameter given to Memory is an integer. Return the size of the Memory to be allocated."""
    # Check if function with the token_value exists which only returns an integer
    for constant in constants:
        if constant.name == token_value:
            return token_value

    # Test if token is an integer
    try:
        int(token_value)
    except ValueError:
        compiler_error("MEMORY_SIZE_VALUE_ERROR", f"The memory size should be an integer. Got: {token_value}")
    return token_value

def get_token_matches(code: str) -> list:
    """Parse tokens that matches a TOKEN_REGEX pattern from a code string. Return list of re.Match objects."""
    TOKEN_REGEX: re.Pattern[str] = re.compile(r'''\[.*\]|".*?"|'.*?'|\S+''')

    matches: List[re.Match[str]]            = list(re.finditer(TOKEN_REGEX, code))
    code_without_comments: str              = re.sub(r'\s*\/\/.*', '', code)  # Take comments out of the code
    final_code_matches: List[re.Match[str]] = list(re.finditer(TOKEN_REGEX, code_without_comments))

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

def get_token_from_match(match: list, file: str, newline_indexes: List[int]) -> Token:
    """Parse Token from a list of re.Match objects. Return the Token."""
    token_value: str        = get_token_value(match.group(0))  # type: ignore
    token_type: TokenType   = get_token_type(token_value)
    token_location          = get_token_location(file, match.start(), newline_indexes)  # type: ignore

    if token_type == TokenType.UINT8:
        token_value = token_value[1:]
    return Token(token_value, token_type, token_location)

def get_token_value(token_value: str) -> str:
    """Bind Intrinsic class value name to Token. Return the Intrinsic value."""
    if token_value == '==':
        return 'EQ'
    if token_value == '>=':
        return 'GE'
    if token_value == '>':
        return 'GT'
    if token_value == '<=':
        return 'LE'
    if token_value == '<':
        return 'LT'
    if token_value == '-':
        return 'MINUS'
    if token_value == '*':
        return 'MUL'
    if token_value == '!=':
        return 'NE'
    if token_value == '+':
        return 'PLUS'
    return token_value

def get_token_type(token_text: str) -> TokenType:
    """Return TokenType value corresponding to the Token.value."""
    keywords: List[str] = [
        'BOOL', 'BREAK', 'CHAR', 'CONST', 'CONTINUE', 'DO', 'DONE', 'ELIF', 'ELSE', 'END',
        'ENDIF', 'FUNCTION', 'IF', 'INT', 'MEMORY', 'PTR', 'STR', 'UINT8', 'WHILE'
    ]
    # Check if all keywords are taken into account
    assert len(Keyword) == len(keywords) , \
        f"Wrong number of keywords in get_token_type function! Expected {len(Keyword)}, got {len(keywords)}"

    # Keywords are case insensitive
    if token_text.upper() in keywords:
        return TokenType.KEYWORD
    if token_text.upper() in {'TRUE', 'FALSE'}:
        return TokenType.BOOL
    if len(token_text) == 3 and token_text[0] == token_text[-1] == "'":
        return TokenType.CHAR
    if token_text.startswith('0x'):
        return TokenType.INT
    if token_text[0] == token_text[-1] == '"':
        return TokenType.STR
    # Numbers 0 - 255
    if re.match(r'u([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])', token_text):
        return TokenType.UINT8
    try:
        _integer = int(token_text)
        return TokenType.INT
    except ValueError:
        return TokenType.WORD

def get_token_location(filename: str, position: int, newline_indexes: List[int]) -> Location:
    """
    Calculate the Position for token based on it's position from the start of the file
    and the indexes of the newline characters found from the file.
    Return Location for Token.
    """
    col: int = position
    row: int = 1
    for i, newline_index in enumerate(newline_indexes):
        if i > 0:
            col = position - newline_indexes[i-1] - 1
            row +=1
        if newline_index > position:
            return (filename, row, col+1)

    if newline_indexes:
        row += 1
        col = position - newline_indexes[-1] - 1
    return (filename, row, col+1)

def get_constants_from_functions(functions: List[Function]) -> List[Constant]:
    """Parse Constants from list of Function objects. Return the list of Constant objects"""
    constants: List[Constant] = []
    for func in functions:
        if len(func.tokens) == 3 and func.signature == ( [], [TokenType.INT] ):
            constant: Constant = Constant(func.name, func.tokens[1].value, func.tokens[1].location)
            constants.append(constant)
    return constants

def remove_unused_constants(tokens: List[Token], constants: List[Constant], memories: List[Memory]) -> List[Constant]:
    """Remove unused constants"""
    return [
        constant for constant in constants \
        if constant.name == 'MEMORY_CAPACITY' \
            or any(constant.value == token.value for token in tokens) \
            or any(constant.name == memory[1] for memory in memories)
        ]
