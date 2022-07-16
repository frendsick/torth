"""
Functions used for generating assembly code from Torth code
"""
import base64
import re
from typing import Dict, List, Optional
from compiler.defs import Constant, Function, Memory, OpType, Op, Program, Token
from compiler.program import generate_program
from compiler.utils import compiler_error, get_parent_op_type_do, get_parent_while
from compiler.utils import get_end_op_for_while, get_related_endif, print_if_verbose

def initialize_asm(constants: List[Constant], memories: List[Memory]) -> str:
    """Initialize assembly code file with some common definitions."""
    return f'''{get_asm_file_start(constants)}
section .bss
  args_ptr: resq 1
  return_stack: resq 1337
  return_stack_len: resq 1
{get_memory_definitions_asm(memories)}
section .text

;; Joinked from Porth's print function, thank you Tsoding!
print:
  mov     r9, -3689348814741910323
  sub     rsp, 40
  lea     rcx, [rsp+30]
.L2:
  mov     rax, rdi
  lea     r8, [rsp+32]
  mul     r9
  mov     rax, rdi
  sub     r8, rcx
  shr     rdx, 3
  lea     rsi, [rdx+rdx*4]
  add     rsi, rsi
  sub     rax, rsi
  add     eax, 48
  mov     BYTE [rcx], al
  mov     rax, rdi
  mov     rdi, rdx
  mov     rdx, rcx
  sub     rcx, 1
  cmp     rax, 9
  ja      .L2
  lea     rax, [rsp+32]
  mov     edi, 1
  sub     rdx, rax
  xor     eax, eax
  lea     rsi, [rsp+32+rdx]
  dec     r8
  mov     rdx, r8
  mov     rax, 1
  syscall
  add     rsp, 40
  ret

'''

def get_asm_file_start(constants: List[Constant]) -> str:
    """Return the contents of the beginning of the generated assembly file."""
    const_defines: str = ''.join(f'%define {const.name} {const.value}\n' for const in constants)

    return f'''default rel

;; DEFINES
%define sys_exit 60
{const_defines}
section .data
'''

def get_asm_file_end() -> str:
    """Returns the contents of the beginning of the generated assembly file"""
    return ''';; -- exit syscall
  mov rax, sys_exit
  pop rdi
  syscall
'''

def get_memory_definitions_asm(memories: List[Memory]) -> str:
    """Generates assembly code of memory definitions. Returns the memory definitions."""
    asm: str = ''
    for memory in memories:
        file, row, col = memory.location
        asm += get_token_info_comment_asm(f'MEMORY {memory.name}', file, row, col)
        asm += f'  {memory.name}: RESB {memory.size}\n'
    return asm

def generate_sub_programs(functions: Dict[str, Function], constants: List[Constant], \
    memories: List[Memory]) -> List[Program]:
    """Generate Program from each Function"""
    sub_programs: List[Program] = []
    for func in functions.values():
        tokens: List[Token] = func.tokens
        sub_programs.append(
            generate_program(tokens, constants, functions, memories)
        )
    return sub_programs

def get_valid_label_for_nasm(function_name: str) -> str:
    """Generate valid NASM label for Function"""
    # Valid characters in labels are letters, numbers, _, $, #, @, ~, ., and ?
    if not re.match(r'^[\w_$#@~.]+$', function_name):
        b64: bytes = base64.b64encode(bytes(function_name, 'utf-8'))
        return str(b64).replace('=','')[2:-1]
    return function_name

def generate_asm(functions: Dict[str, Function], \
    constants: List[Constant], memories: List[Memory], is_verbose: bool) -> str:
    """Generate Assembly from Functions."""
    assembly: str = initialize_asm(constants, memories)
    #tokens: List[Token] = get_tokens_from_functions(functions)
    for func in functions.values():
        # Generate Program from Function
        sub_program: Program = generate_program(func.tokens, constants, functions, memories)

        # Type check the program
        print_if_verbose(f"Type checking function {func.name}", is_verbose)
        # type_check_function(func, sub_program, functions)

        # Generate Assembly from Function
        function_name: str = get_valid_label_for_nasm(func.name)
        if func.name.upper() == 'MAIN':
            assembly +=  'global _start\n'
            assembly +=  '_start:\n'
            assembly +=  '  mov [args_ptr], rsp   ; Pointer to argc\n'
        else:
            assembly += f'{function_name}:\n'
            assembly += f';; [{function_name}] Save the return address to return_stack\n'
            assembly +=  '  pop rax\n'
            assembly +=  '  mov rbx, return_stack\n'
            assembly +=  '  add rbx, [return_stack_len]\n'
            assembly +=  '    mov [rbx], rax\n'
            assembly +=  '  add qword [return_stack_len], 8  ; Increment return_stack_len\n'

        assembly = generate_program_asm(sub_program, assembly)

        # Jump to the return address stored in r15 register
        if function_name.upper() != 'MAIN':
            assembly +=  ';; Jump to the return address found in return_stack\n'
            assembly +=  '  sub qword [return_stack_len], 8  ; Decrement return_stack_len\n'
            assembly +=  '  mov rax, return_stack\n'
            assembly +=  '  add rax, [return_stack_len]\n'
            assembly +=  '  jmp [rax]  ; Return\n'
        else:
            assembly += get_asm_file_end()
    return assembly

def generate_program_asm(program: Program, assembly: str) -> str:
    """Generate assembly file and write it to a file."""
    for op in program:
        assembly += get_op_comment_asm(op, op.type)
        if op.type == OpType.PUSH_STR:
            assembly = add_string_variable_asm(assembly, op.token.value, op)

        # Get assembly for the current Op
        op_asm: str = get_op_asm(op, program=program)
        if op_asm != "":
            assembly += op_asm
    return f"{assembly}"

def get_op_asm(op: Op, program: Program) -> str:
    """Generate assembly code for certain Op. Return assembly for the Op."""
    if op.type in {
        OpType.CAST_BOOL,   # Casts affect only the type checking
        OpType.CAST_CHAR,
        OpType.CAST_INT,
        OpType.CAST_PTR,
        OpType.CAST_STR,
        OpType.CAST_UINT8,
        OpType.IF           # If is just a keyword which starts an IF-block
        }:
        return ''
    if op.type == OpType.BREAK:
        return get_break_asm(op, program)
    if op.type == OpType.CONTINUE:
        return get_continue_asm(op, program)
    if op.type == OpType.DO:
        return get_do_asm(op, program)
    if op.type == OpType.DONE:
        return get_done_asm(op, program)
    if op.type == OpType.ELIF:
        return get_elif_asm(op, program)
    if op.type == OpType.ELSE:
        return get_else_asm(op, program)
    if op.type == OpType.ENDIF:
        return get_endif_asm(op)
    if op.type == OpType.FUNCTION_CALL:
        return get_function_call_asm(op)
    if op.type == OpType.PUSH_BOOL:
        return get_push_bool_asm(op.token.value.upper())
    if op.type == OpType.PUSH_CHAR:
        return get_push_char_asm(op)
    if op.type == OpType.PUSH_INT:
        return get_push_int_asm(op.token.value)
    if op.type == OpType.PUSH_PTR:
        return get_push_ptr_asm(op.token.value)
    if op.type == OpType.PUSH_STR:
        return get_push_str_asm(op)
    if op.type == OpType.PUSH_UINT8:
        return get_push_int_asm(op.token.value)
    if op.type == OpType.WHILE:
        return get_while_asm(op)
    if op.type == OpType.INTRINSIC:
        intrinsic: str = op.token.value.upper()
        if intrinsic == "AND":
            return get_and_asm()
        if intrinsic == "ARGC":
            return get_argc_asm()
        if intrinsic == "ARGV":
            return get_argv_asm()
        if intrinsic == "DIVMOD":
            return get_divmod_asm()
        if intrinsic == "DROP":
            return get_drop_asm()
        if intrinsic == "DUP":
            return get_dup_asm()
        if intrinsic == "ENVP":
            return get_envp_asm()
        if intrinsic == "EQ":
            return get_eq_asm()
        if intrinsic == "GE":
            return get_ge_asm()
        if intrinsic == "GT":
            return get_gt_asm()
        if intrinsic == "LE":
            return get_le_asm()
        if intrinsic == "LT":
            return get_lt_asm()
        if intrinsic.startswith("LOAD_"):
            return get_load_asm(intrinsic)
        if intrinsic == "MINUS":
            return get_minus_asm()
        if intrinsic == "MUL":
            return get_mul_asm()
        if intrinsic == "NE":
            return get_ne_asm()
        if intrinsic == "NTH":
            return get_nth_asm()
        if intrinsic == "OR":
            return get_or_asm()
        if intrinsic == "OVER":
            return get_over_asm()
        if intrinsic == "PLUS":
            return get_plus_asm()
        if intrinsic == "PRINT":
            return get_print_asm()
        if intrinsic == "ROT":
            return get_rot_asm()
        if intrinsic.startswith("STORE_"):
            return get_store_asm(intrinsic)
        if intrinsic == "SWAP":
            return get_swap_asm()
        if intrinsic == "SYSCALL0":
            return get_syscall_asm(param_count=0)
        if intrinsic == "SYSCALL1":
            return get_syscall_asm(param_count=1)
        if intrinsic == "SYSCALL2":
            return get_syscall_asm(param_count=2)
        if intrinsic == "SYSCALL3":
            return get_syscall_asm(param_count=3)
        if intrinsic == "SYSCALL4":
            return get_syscall_asm(param_count=4)
        if intrinsic == "SYSCALL5":
            return get_syscall_asm(param_count=5)
        if intrinsic == "SYSCALL6":
            return get_syscall_asm(param_count=6)

        # Compiler error for Intrinsic not implemented
        compiler_error("NOT_IMPLEMENTED", f"Intrinsic '{intrinsic}' has not been implemented.", op.token)
    # Compiler error for Op not implemented
    compiler_error("NOT_IMPLEMENTED", f"Operand '{op.type.name}' has not been implemented.", op.token)

def get_op_comment_asm(op: Op, op_type: OpType) -> str:
    """Generate assembly comment for the Op. Return the comment string."""
    # Function calls and returns should not generate any output
    op_name: str    = op_type.name
    src_file: str   = op.token.location[0]
    row: int        = op.token.location[1]
    col: int        = op.token.location[2]
    if op_name == "INTRINSIC":
        op_name = f'{op_name} {op.token.value}'
    elif op_name == "FUNCTION_CALL":
        op_name = f'Call {op.token.value}'
    return get_token_info_comment_asm(op_name, src_file, row, col, function_name=op.func.name)

def get_token_info_comment_asm(name: str, file: str, row: int, col: int, function_name: Optional[str] = None) -> str:
    """Return formatted informative string for the current Op"""
    if function_name:
        return f';; [{function_name}] {name} | File: {file}, Row: {row}, Col: {col}' + '\n'
    return f';; -- {name} | File: {file}, Row: {row}, Col: {col}' + '\n'

def get_comparison_asm(cmov_operand: str) -> str:
    """
    Generate assembly code for different comparison Intrinsics, like EQ.
    Only cmov operand changes with different comparison intrinsics.
    Return the assembly code for certain comparison intrinsic.
    """
    comparison_asm: str  =  '  pop rax\n'
    comparison_asm      +=  '  pop rbx\n'
    comparison_asm      +=  '  mov rcx, 0\n'
    comparison_asm      +=  '  mov rdx, 1\n'
    comparison_asm      +=  '  cmp rax, rbx\n'
    comparison_asm      += f'  {cmov_operand} rcx, rdx\n'
    comparison_asm      +=  '  push rcx\n'
    return comparison_asm

def get_arithmetic_asm(operand: str) -> str:
    """Return the assembly code for different arithmetic Intrinsics, like PLUS."""
    arithmetic_asm: str  =  '  pop rbx\n'
    arithmetic_asm      +=  '  pop rax\n'
    arithmetic_asm      += f'  {operand} rax, rbx\n'
    arithmetic_asm      +=  '  push rax\n'
    return arithmetic_asm

def format_escape_sequence_characters_for_nasm(string: str) -> str:
    """Transform escape sequence characters to a format supported by NASM."""
    # Make temporary value for escaped backslashes
    string = string.replace('\\\\','<backslash>')

    # Handle escape sequence characters
    string = string.replace('\\t','",9,"')          # Tab
    string = string.replace('\\n','",10,"')         # Newline
    string = string.replace('\\r','",13,"')         # Carriage return
    string = string.replace('\\e','",27,"')         # Escape

    # Escaped backslash to a singular backslash
    string = string.replace('<backslash>','\\')
    return string

def add_string_variable_asm(assembly: str, string: str, op: Op) -> str:
    """Writes a new string variable to assembly file in the .rodata section."""
    data_section: str = 'section .data\n'
    string_index = assembly.find(data_section) + len(data_section)

    # Replace \n with nasm approved 10s for newline
    escaped_string: str = format_escape_sequence_characters_for_nasm(string)
    return f'{assembly[:string_index]}  {op.func.name}_s{op.id} db {escaped_string},0\n{assembly[string_index:]}'

def get_do_asm(op: Op, program: Program) -> str:
    """DO is conditional jump to operand after ELIF, ELSE, END or ENDIF."""
    parent_op_type: OpType = get_parent_op_type_do(op, program)

    # Keeping the count of duplicate parent Ops allows for nested IF or WHILE blocks
    parent_op_count: int = 0
    op_asm: str = ''
    for i in range(op.id + 1, len(program)):
        op_type: OpType = program[i].type

        # Keep count on the nested IF's or WHILE's
        if (parent_op_type in [OpType.IF, OpType.ELIF] and op_type == OpType.IF) \
        or (parent_op_type == OpType.WHILE and op_type == OpType.WHILE):
            parent_op_count += 1
            continue

        if parent_op_count == 0 and \
            ( ( parent_op_type == OpType.IF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF)) \
            or ( parent_op_type == OpType.ELIF and op_type in (OpType.ELIF, OpType.ELSE, OpType.ENDIF)) \
            or ( parent_op_type == OpType.WHILE and op_type == OpType.DONE ) ):
            jump_destination: str = f'{op.func.name}_{program[i].type.name}{i}'
            op_asm = generate_do_asm(jump_destination)
            break

        # Decrement counter when passing another block's ENDIF / DONE
        if (parent_op_type in [OpType.IF, OpType.ELIF] and op_type == OpType.ENDIF) \
        or (parent_op_type == OpType.WHILE and op_type == OpType.DONE):
            parent_op_count -= 1

    if not op_asm:
        block_type: str = 'WHILE' if parent_op_type == OpType.WHILE else 'IF'
        block_end: str  = 'DONE'  if parent_op_type == OpType.WHILE else 'ENDIF'
        compiler_error("UNCLOSED_BLOCK", f"The current {block_type} block is missing {block_end} keyword.", op.token)
    return op_asm

def get_break_asm(op: Op, program: Program) -> str:
    """BREAK is an unconditional jump to operand after current loop's DONE."""
    parent_while: Op = get_parent_while(op, program)
    parent_end:   Op = get_end_op_for_while(parent_while, program)
    return f'  jmp {op.func.name}_DONE{parent_end.id}\n'

def get_continue_asm(op: Op, program: Program) -> str:
    """CONTINUE is an unconditional jump to current loop's WHILE."""
    parent_while: Op = get_parent_while(op, program)
    op_asm: str  = f'  jmp {op.func.name}_WHILE{parent_while.id}\n'
    op_asm      += f'{op.func.name}_DONE{op.id}:\n'
    return op_asm

def generate_do_asm(jump_destination: str) -> str:
    """DO pops an element from the stack and checks if it is zero."""
    op_asm: str  =  '  pop rax\n'
    op_asm      +=  '  test rax, rax\n'
    op_asm      += f'  jz {jump_destination}\n'
    return op_asm

def get_done_asm(op: Op, program: Program) -> str:
    """DONE is an unconditional jump to current loop's WHILE."""
    parent_while: Op = get_parent_while(op, program)
    op_asm: str  = f'  jmp {op.func.name}_WHILE{parent_while.id}\n'
    op_asm      += f'{op.func.name}_DONE{op.id}:\n'
    return op_asm

def get_elif_asm(op: Op, program: Program) -> str:
    """ELIF is an unconditional jump to ENDIF and a keyword for DO to jump to."""
    related_endif: Op = get_related_endif(op, program)
    op_asm: str  = f'  jmp {op.func.name}_ENDIF{related_endif.id}\n'
    op_asm      += f'{op.func.name}_ELIF{op.id}:\n'
    return op_asm

def get_else_asm(op: Op, program: Program) -> str:
    """ELSE is an unconditional jump to ENDIF and a keyword for DO to jump to."""
    related_endif: Op = get_related_endif(op, program)
    op_asm: str  = f'  jmp {op.func.name}_ENDIF{related_endif.id}\n'
    op_asm      += f'{op.func.name}_ELSE{op.id}:\n'
    return op_asm

def get_endif_asm(op: Op) -> str:
    """ENDIF is a keyword for DO, ELIF or ELSE to jump to without additional functionality."""
    return f'{op.func.name}_ENDIF{op.id}:\n'

def get_function_call_asm(op: Op) -> str:
    """Generate assembly for calling a function"""
    return f"  call {get_valid_label_for_nasm(op.token.value)}\n"

def get_push_bool_asm(boolean: str) -> str:
    """Return the assembly code for PUSH_BOOL Operand."""
    integer: int = 1 if boolean == 'TRUE' else 0
    op_asm: str  = f'  mov rax, {integer}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_char_asm(op: Op) -> str:
    """Return the assembly code for PUSH_CHAR Operand."""
    op_asm: str  = f'  mov rax, {ord(op.token.value[1])}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_int_asm(integer: str) -> str:
    """Return the assembly code for PUSH_INT Operand."""
    op_asm: str  = f'  mov rax, {integer}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_ptr_asm(memory_name: str) -> str:
    """Return the assembly code for PUSH_PTR Operand."""
    op_asm: str  = f'  mov rax, {memory_name}\n'
    op_asm      +=  '  push rax\n'
    return op_asm

def get_push_str_asm(op: Op) -> str:
    """Pushes a pointer to the string variable to the stack."""
    op_asm: str  = f'  mov rsi, {op.func.name}_s{op.id} ; Pointer to string\n'
    op_asm      +=  '  push rsi\n'
    return op_asm

def get_while_asm(op: Op) -> str:
    """
    WHILE is a keyword for DONE to jump to.
    Return the assembly code for WHILE Operand.
    """
    return f'{op.func.name}_WHILE{op.id}:\n'

def get_and_asm() -> str:
    """AND performs bitwise-AND operation to two integers."""
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  and rbx, rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_argc_asm() -> str:
    """ARGC pushes the argument count to the stack."""
    op_asm: str  = '  mov rax, [args_ptr]\n'
    op_asm      += '  mov rax, [rax]\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_argv_asm() -> str:
    """ARGV pushes the pointer to argument array to the stack."""
    op_asm: str  = '  mov rax, [args_ptr]\n'
    op_asm      += '  add rax, 8\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_divmod_asm() -> str:
    """DIVMOD pops two integers from the stack and pushes their remainder and quotient."""
    op_asm: str  = '  xor edx, edx ; Do not use floating point arithmetic\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rax\n'
    op_asm      += '  div rbx\n'
    op_asm      += '  push rdx ; Remainder\n'
    op_asm      += '  push rax ; Quotient\n'
    return op_asm

def get_drop_asm() -> str:
    """DROP removes one element from the stack."""
    return '  add rsp, 8\n'

def get_dup_asm() -> str:
    """
    DUP duplicates the top element in the stack.
    Example with the stack's top element being the rightmost: a -> a a
    """
    op_asm: str  = '  pop rax\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_envp_asm() -> str:
    """ENVP pushes the environment pointer to the stack."""
    op_asm: str  = '  mov rax, [args_ptr]\n'
    op_asm      += '  add rax, 24\n'
    op_asm      += '  push rax\n'
    return op_asm

def get_eq_asm() -> str:
    """
    EQ takes two elements from the stack and checks if they are equal.
    It pushes the second element to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmove")

def get_ge_asm() -> str:
    """
    GE takes two elements from the stack and checks if the top element >= the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmovge")

def get_gt_asm() -> str:
    """
    GT takes two elements from the stack and checks if the top element > the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmovg")

def get_le_asm() -> str:
    """
    LE takes two elements from the stack and checks if the top element <= the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmovle")

def get_lt_asm() -> str:
    """
    LT takes two elements from the stack and checks if the top element < the other.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmovl")

def get_load_asm(load_variant: str) -> str:
    """
    LOAD variants load certain size value from where a pointer is pointing to.
    It takes one pointer from the stack and pushes back the dereferenced pointer value.
    Different LOAD variants: LOAD_BYTE, LOAD_WORD, LOAD_DWORD, LOAD_QWORD
    """
    variant_register_sizes: Dict[str, str] = {
        'LOAD_BYTE'    : 'bl',
        'LOAD_WORD'    : 'bx',
        'LOAD_DWORD'   : 'ebx',
        'LOAD_QWORD'   : 'rbx'
    }
    register: str = variant_register_sizes[load_variant]
    op_asm: str  =  '  pop rax\n'
    op_asm      +=  '  xor rbx, rbx\n'
    op_asm      += f'  mov {register}, [rax]\n'
    op_asm      +=  '  push rbx\n'
    return op_asm

def get_minus_asm() -> str:
    """Pop two integers from the stack and decrement the second value from the top one."""
    return get_arithmetic_asm("sub")

def get_mul_asm() -> str:
    """Pop two integers from the stack and push the product of the two values."""
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  mul rbx\n'
    op_asm      += '  push rax  ; Product\n'
    return op_asm

def get_ne_asm() -> str:
    """
    NE takes two elements from the stack and checks if the values are not equal.
    It pushes the second element back to the stack and a boolean value of the comparison.
    """
    return get_comparison_asm("cmovne")

# Copies Nth element from the stack to the top of the stack
def get_nth_asm() -> str:
    """
    NTH pops one integer from the stack and pushes the Nth element from stack back to stack.
    Note that the Nth is counted without the popped integer.
    Example: 30 20 10 3 NTH print  // Output: 30 (because 30 is 3rd element without the popped 3).
    """
    op_asm: str  = '  pop rax\n'
    op_asm      += '  sub rax, 1\n'
    op_asm      += '  mov rbx, 8\n'
    op_asm      += '  mul rbx\n'
    op_asm      += '  add rsp, rax ; Stack pointer to the Nth element\n'
    op_asm      += '  pop rbx      ; Get Nth element to rax\n'
    op_asm      += '  add rax, 8\n'
    op_asm      += '  sub rsp, rax ; Return stack pointer\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_or_asm() -> str:
    """OR performs bitwise-OR operation to two integers."""
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  or rbx, rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_over_asm() -> str:
    """
    OVER Intrinsic pushes a copy of the second element of the stack.
    Example with the stack's top element being the rightmost: a b -> a b a
    """
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_plus_asm() -> str:
    """Pop two integers from the stack and push the sum of the two values."""
    return get_arithmetic_asm("add")

def get_print_asm() -> str:
    """Pop an integer from the stack and print the value of it to the stdout."""
    op_asm: str  =  '  pop rdi\n'
    op_asm      +=  '  call print\n'
    return op_asm

def get_rot_asm() -> str:
    """
    ROT Intrinsic rotates the top three elements of the stack so that the third becomes first.
    Example with the stack's top element being the rightmost: a b c -> b c a
    """
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  pop rcx\n'
    op_asm      += '  push rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rcx\n'
    return op_asm

def get_store_asm(store_variant: str) -> str:
    """
    STORE variants store certain size value from where a pointer is pointing to.
    It takes a pointer and a value from the stack and loads the value to the pointer address.
    Different STORE variants: STORE_BYTE, STORE_WORD, STORE_DWORD, STORE_QWORD
    """
    variant_register_sizes: Dict[str, str] = {
        'STORE_BYTE'    : 'bl',
        'STORE_WORD'    : 'bx',
        'STORE_DWORD'   : 'ebx',
        'STORE_QWORD'   : 'rbx'
    }
    register: str = variant_register_sizes[store_variant]
    op_asm: str  =  '  pop rax\n'
    op_asm      +=  '  pop rbx\n'
    op_asm      += f'  mov [rax], {register}\n'
    return op_asm

def get_swap_asm() -> str:
    """
    SWAP Intrinsic swaps two top elements in the stack.
    Example with the stack's top element being the rightmost: a b -> b a
    """
    op_asm: str  = '  pop rax\n'
    op_asm      += '  pop rbx\n'
    op_asm      += '  push rax\n'
    op_asm      += '  push rbx\n'
    return op_asm

def get_syscall_asm(param_count: int) -> str:
    """
    SYSCALL intrinsic variants call a Linux syscall.
    Syscalls require different amount of arguments from 0 to 6.
    Different variants are named SYSCALL0 - SYSCALL6 by the amount of arguments.
    The different syscall constants required for RAX register can be found from lib/sys.torth.
    Naming convention (case sensitive): SYS_<syscall> - Example: SYS_write

    https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#tables
    """
    op_asm: str  = "  pop rax ; syscall\n"

    # Pop arguments to syscall argument registers
    argument_registers: List[str] = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']
    for i in range(param_count):
        op_asm += f"  pop {argument_registers[i]} ; {i+1}. arg\n"

    # Call the syscall and push return code to RAX
    op_asm      += "  syscall\n"
    op_asm      += "  push rax ; return code\n"
    return op_asm
