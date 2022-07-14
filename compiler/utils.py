"""
Utility functions for Torth compiler
"""
import argparse
import subprocess
import os
import sys
from typing import List, NoReturn, Optional
from compiler.defs import COLORS, Function, Op, OpType, Program, Token, TokenType, TypeStack

def usage() -> NoReturn:
    """Print usage message and exit with non-zero exit code"""
    print("Usage: ./torth.py file")
    sys.exit(1)

def get_command_line_arguments() -> argparse.Namespace:
    """Initialize ArgumendParser with command-line arguments and return the parser's Namespace"""
    parser = argparse.ArgumentParser(description='Compile Torth code')
    parser.add_argument('-o', '--out', help='Output file', metavar='FILE')
    parser.add_argument('-p', '--path', metavar='DIRS', \
        help='Comma separated list of directories to be added to PATH in addition of the default "lib"')
    parser.add_argument('-d', '--debug', action='store_true', \
        help="Do not strip the resulting binary")
    parser.add_argument('-g', '--graph', action='store_true', \
        help="Generate Graphviz graph from the program's control flow")
    parser.add_argument('-r', '--run', action='store_true', \
        help="Run program after compilation")
    parser.add_argument('-s', '--save-asm', action='store_true', \
        help="Save assembly file named after code_file with .asm extension")
    parser.add_argument('-v', '--verbose', action='store_true', \
        help="Output compilation steps")
    parser.add_argument('code_file', help='Input file')

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    if not os.path.isfile(args.code_file):
        compiler_error("ARGUMENT_ERROR", f"Argument '{args.code_file}' is not a file")
    return args

def get_file_contents(file_name: str) -> str:
    """Open a file in read-only mode and return the contents"""
    with open(file_name, 'r', encoding='utf8') as f:
        return f.read()

def compiler_error(error_type: str, error_message: str, token: Optional[Token] = None, \
    current_stack: Optional[TypeStack] = None) -> NoReturn:
    """Output compiler error message to the console and exit with non-zero exit code"""
    print(f"{COLORS['HEADER']}Compiler error {COLORS['FAIL']}{error_type}{COLORS['NC']}" \
        + f":\n{error_message}")
    if current_stack:
        print(f"\nCurrent stack state:\n{current_stack.repr()}")
    if token:
        print(get_token_location_info(token))
    sys.exit(1)

def print_if_verbose(message: str, is_verbose: bool) -> None:
    """Print message if --verbose compiler argument is present"""
    if is_verbose:
        print(f"[{COLORS['HEADER']}VERBOSE{COLORS['NC']}] {message}")

def get_token_location_info(token: Token) -> str:
    """Returns a string containing Token object's location in the source code"""
    return f'''
{COLORS['HEADER']}Operand{COLORS['NC']}: {token.value}
{COLORS['HEADER']}File{COLORS['NC']}: {token.location[0]}
{COLORS['HEADER']}Row{COLORS['NC']}: {token.location[1]}
{COLORS['HEADER']}Column{COLORS['NC']}: {token.location[2]}'''

def handle_arguments(input_file: str, executable_file: str, program: Program, args) -> None:
    """Handle special command line arguments"""
    if args.graph:
        print_if_verbose("Generating Graphviz graph from the program", args.verbose)
        generate_graph_file(input_file, program)
    if args.run:
        print_if_verbose(f"Running the executable {executable_file}", args.verbose)
        run_code(executable_file)

def function_exists(function_name: str, functions: List[Function]) -> bool:
    """Check if there is a Function with a certain name"""
    return any(function_name == func.name for func in functions)

def generate_graph_file(input_file: str, program: Program) -> None:
    """Generate SVG file displaying the control flow of the program"""
    graph_contents: str = get_graph_contents(program)
    base_file_name: str = input_file.replace('.torth', '')
    with open(f'{base_file_name}.dot', 'w', encoding='utf-8') as f:
        f.write(graph_contents)
    subprocess.run(['dot', '-Tsvg', f'-o{base_file_name}.svg', f'{base_file_name}.dot'], check=True)
    subprocess.run(['rm', '-f', f'{base_file_name}.dot'], check=True)

def run_code(executable_file: str) -> None:
    """Run an executable"""
    subprocess.run([f'./{executable_file}'], check=True)

def get_graph_contents(program: Program) -> str:
    """Return Graphviz graph from Program's control flow"""
    graph_contents: str = initialize_graph(program)

    for op in program:
        if op.type == OpType.BREAK:
            graph_contents += get_graph_row_break(op, program)
        elif op.type == OpType.CONTINUE:
            graph_contents += get_graph_row_continue(op, program)
        elif op.type == OpType.DO:
            graph_contents += get_graph_row_do(op, program)
        elif op.type == OpType.DONE:
            graph_contents += get_graph_row_done(op, program)
        elif op.type == OpType.ELIF:
            graph_contents += get_graph_row_elif(op, program)
        elif op.type == OpType.ELSE:
            graph_contents += get_graph_row_else(op, program)
        else:
            graph_contents += f'  node{op.id} -> node{op.id+1};\n'

    graph_contents += '}'
    return graph_contents

def initialize_graph(program: Program) -> str:
    """Generates a node id for each Op in Program in Graphviz format"""
    graph_contents: str = 'digraph Program {\n'
    for i, op in enumerate(program):
        label_top_row: str = str(op.type)
        if op.type == OpType.INTRINSIC:
            label_top_row = f"{op.type} '{op.token.value}'"
        elif op.type in {OpType.FUNCTION_CALL, OpType.FUNCTION_RETURN}:
            function_name: str = op.token.value.replace('_CALL', '').replace('_RETURN', '')
            label_top_row = f"{op.type} '{function_name}'"

        graph_contents += f'  node{i} [label = "{label_top_row}\n{op.token.location}"];\n'
    graph_contents += f'  node{len(program)} [label = "PROGRAM EXIT"];\n'
    return graph_contents

def get_graph_row_break(op: Op, program: Program) -> str:
    """BREAK is an unconditional jump to operand after current loop's END."""
    parent_while: Op = get_parent_while(op, program)
    parent_end:   Op = get_end_op_for_while(parent_while, program)
    return f'  node{op.id} -> node{parent_end.id+1};\n'

def get_graph_row_continue(op: Op, program: Program) -> str:
    """CONTINUE is an unconditional jump to current loop's WHILE."""
    parent_while: Op = get_parent_while(op, program)
    return f'  node{op.id} -> node{parent_while.id};\n'

def get_graph_row_do(op: Op, program: Program) -> str:
    """DO is conditional jump to operand after ELIF, ELSE, END or ENDIF."""
    parent_op_type: OpType = get_parent_op_type_do(op, program)
    # Keeping the count of duplicate parent Ops allows for nested IF or WHILE blocks
    parent_op_count: int = 0
    graph_contents: str  = ''
    for j in range(op.id + 1, len(program)):
        op_type: OpType = program[j].type

        # Keep count on the nested IF's or WHILE's
        if (parent_op_type in [OpType.IF, OpType.ELIF] and op_type == OpType.IF) \
        or (parent_op_type == OpType.WHILE and op_type == OpType.WHILE):
            parent_op_count += 1
            continue

        if parent_op_count == 0 and \
            ( ( parent_op_type == OpType.IF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF)) \
            or ( parent_op_type == OpType.ELIF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF)) \
            or ( parent_op_type == OpType.WHILE and op_type == OpType.DONE ) ):
            graph_contents += f'  node{op.id} -> node{j+1};\n'
            graph_contents += f'  node{op.id} -> node{op.id+1};\n'
            return graph_contents

        # Decrement counter when passing another block's ENDIF / DONE
        if (parent_op_type in [OpType.IF, OpType.ELIF] and op_type == OpType.ENDIF) \
        or (parent_op_type == OpType.WHILE and op_type == OpType.DONE):
            parent_op_count -= 1

    compiler_error('GRAPH_ERROR', \
        'Unknown error occurred while generating Graphviz graph for DO keyword', op.token)

def get_graph_row_done(op: Op, program: Program) -> str:
    """DONE is an unconditional jump to current loop's WHILE."""
    parent_while: Op = get_parent_while(op, program)
    return f'  node{op.id} -> node{parent_while.id};\n'

def get_graph_row_elif(op: Op, program: Program) -> str:
    """ELIF is an unconditional jump to ENDIF and a keyword for DO to jump to."""
    for j in range(op.id + 1, len(program)):
        if program[j].type == OpType.ENDIF:
            return f'  node{op.id} -> node{j+1};\n'
    compiler_error('GRAPH_ERROR', \
        'Unknown error occurred while generating Graphviz graph for ELIF keyword', op.token)

def get_graph_row_else(op: Op, program: Program) -> str:
    """ELSE is an unconditional jump to ENDIF and a keyword for DO to jump to."""
    for j in range(op.id + 1, len(program)):
        if program[j].type == OpType.ENDIF:
            return f'  node{op.id} -> node{j+1};\n'
    compiler_error('GRAPH_ERROR', \
        'Unknown error occurred while generating Graphviz graph for ELSE keyword', op.token)

def get_related_endif(op: Op, program: Program) -> Op:
    """Returns the current loop's ENDIF Operand for the current Operand."""
    if_count: int = 0
    for i in range(op.id+1, len(program)):
        if program[i].type == OpType.ENDIF:
            if if_count == 0:
                return program[i]
            if_count -= 1
        elif program[i].type == OpType.IF:
            if_count += 1

    compiler_error(f"AMBIGUOUS_{op.token.value.upper()}", \
        f"{op.token.value.upper()} operand without parent WHILE.", op.token)

def get_parent_while(op: Op, program: Program) -> Op:
    """Returns the parent WHILE Operand for the current Operand."""
    done_count: int = 0
    for i in range(op.id - 1, -1, -1):
        if program[i].type == OpType.WHILE:
            if done_count == 0:
                return program[i]
            done_count -= 1
        if program[i].type == OpType.DONE:
            done_count += 1

    compiler_error(f"AMBIGUOUS_{op.token.value.upper()}", \
        f"{op.token.value.upper()} operand without parent WHILE.", op.token)

def get_end_op_for_while(op: Op, program: Program) -> Op:
    """Returns the END Operand for the current WHILE Operand which closes the WHILE loop."""
    while_count: int = 0
    for i in range(op.id, len(program)):
        if program[i].type == OpType.DONE:
            while_count -= 1
            if while_count == 0:
                return program[i]
        if program[i].type == OpType.WHILE:
            while_count += 1
    compiler_error("AMBIGUOUS_BREAK", "WHILE loop does not have DONE.", op.token)

def get_parent_op_type_do(op: Op, program: Program) -> OpType:
    """Get the parent OpType for the current DO Operand like IF or WHILE"""
    parent_count: int = 0
    for i in range(op.id - 1, -1, -1):
        if program[i].type in (OpType.IF, OpType.ELIF, OpType.WHILE):
            if parent_count == 0:
                return program[i].type
            parent_count -= 1
        if program[i].type in (OpType.DONE, OpType.ENDIF):
            parent_count += 1
    compiler_error("AMBIGUOUS_DO", "DO operand without parent IF, ELIF or WHILE", op.token)

def equal_type_lists(type_list1: List[TokenType], type_list2: List[TokenType]) -> bool:
    """Check if two Lists of TokenTypes are equal without checking ANY types."""
    if len(type_list1) != len(type_list2):
        return False
    for t1, t2 in zip(type_list1, type_list2):
        if TokenType.ANY in {t1, t2}:
            continue
        if t1 != t2:
            return False
    return True
