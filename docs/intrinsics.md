# Intrinsics

Intrinsics are built-in functions that generate static assembly output. The key difference between a [keyword](keywords.md) and an intrinsic is that the behavior of a keyword is dependent on other words in the program whereas an intrinsic will always generate the same assembly output regardless of the context in which it is used.

## List of Intrinsics

- [AND](#AND)
- [ARGC](#ARGC)
- [ARGV](#ARGV)
- [DIVMOD](#DIVMOD)
- [DROP](#DROP)
- [DUP](#DUP)
- [ENVP](#ENVP)
- [EQ](#EQ)
- [GE](#GE)
- [GT](#GT)
- [LE](#LE)
- [LOAD_BOOL](#LOAD_BOOL)
- [LOAD_CHAR](#LOAD_CHAR)
- [LOAD_INT](#LOAD_INT)
- [LOAD_PTR](#LOAD_PTR)
- [LOAD_STR](#LOAD_STR)
- [LOAD_UINT8](#LOAD_UINT8)
- [LT](#LT)
- [MINUS](#MINUS)
- [MUL](#MUL)
- [NE](#NE)
- [NOT](#NOT)
- [NTH](#NTH)
- [OR](#OR)
- [OVER](#OVER)
- [PLUS](#PLUS)
- [PRINT](#PRINT)
- [ROT](#ROT)
- [STORE_BOOL](#STORE_BOOL)
- [STORE_CHAR](#STORE_CHAR)
- [STORE_INT](#STORE_INT)
- [STORE_PTR](#STORE_PTR)
- [STORE_STR](#STORE_STR)
- [STORE_UINT8](#STORE_UINT8)
- [SWAP](#SWAP)
- [SWAP2](#SWAP2)
- [SYSCALL0](#SYSCALL0)
- [SYSCALL1](#SYSCALL1)
- [SYSCALL2](#SYSCALL2)
- [SYSCALL3](#SYSCALL3)
- [SYSCALL4](#SYSCALL4)
- [SYSCALL5](#SYSCALL5)
- [SYSCALL6](#SYSCALL6)

## AND

Perform bitwise AND for two [integer](definitions.md#integer-types) values.

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Perform bitwise AND operation to the popped values
3. Push the result of the bitwise operator as [INT](types.md#int-uint8---integer)

## ARGC

Push the command line argument count to the stack.

## ARGV

Push the pointer to the command line argument array to the stack.

## DIVMOD

Perform a division operation for two [integers](definitions.md#integer-types) and push both the remainder and the quotient to the stack.

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Perform a division operation to the popped values
3. Push remainder
4. Push quotient

## DROP

Remove the top element from the stack.

## ENVP

Push the environment pointer to the stack.
