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
- [EQ](#Comparisons)
- [GE](#Comparisons)
- [GT](#Comparisons)
- [LE](#Comparisons)
- [LOAD_BOOL](#LOAD_BOOL)
- [LOAD_CHAR](#LOAD_CHAR)
- [LOAD_INT](#LOAD_INT)
- [LOAD_PTR](#LOAD_PTR)
- [LOAD_STR](#LOAD_STR)
- [LOAD_UINT8](#LOAD_UINT8)
- [LT](#Comparisons)
- [MINUS](#Calculations)
- [MUL](#Calculations)
- [NE](#Comparisons)
- [NTH](#NTH)
- [OR](#OR)
- [OVER](#OVER)
- [PLUS](#Calculations)
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

## Calculations

Perform a calculation operation for two [integers](definitions.md#integer-types) and push the result.

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Perform a calculation operation to the popped values
3. Push result

Different calculation intrinsics:

- PLUS (+)
- MINUS (-)
- MUL (\*)

## Comparisons

Perform a certain comparison operation to two [integers](definitions.md#integer-types).

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Push the result of the comparison as [BOOL](types.md#bool---boolean)

Different comparison intrinsics:

- **EQ**: Equal (==)
- **GE**: Greater than or equal (>=)
- **GT**: Greater than (>)
- **LE**: Less than or equal (<=)
- **LT**: Less than (<)
- **NE**: Not equal (!=)

## AND

Perform bitwise AND for two [integer](definitions.md#integer-types) values.

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Perform bitwise AND operation to the popped values
3. Push the result of the bitwise operation as [INT](types.md#int-uint8---integer)

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

## LOAD

LOAD-intrinsics pushes a value pointed by a [pointer](types.md#ptr---pointer) type value to the stack. The type of the pushed value depends of the used LOAD-intrinsic.

1. Pop a [PTR](types.md#ptr---pointer) type value from the stack
2. Push the value pointed by the popped pointer to the stack

Different LOAD-intrinsics:

- LOAD_BOOL
- LOAD_CHAR
- LOAD_INT
- LOAD_PTR
- LOAD_STR
- LOAD_UINT8

## NTH

Pop one [integer](definitions.md#integer-types) from the stack and push the Nth element from stack. The "Nth" is counted without the popped integer starting from 1.

```
30 20 10 3 NTH print // Output: 30 (30 is 3rd element without the popped 3).
```

## OR

Perform bitwise OR for two [integer](definitions.md#integer-types) values.

1. Pop two [integers](definitions.md#integer-types) from the stack
2. Perform bitwise OR operation to the popped values
3. Push the result of the bitwise operation as [INT](types.md#int-uint8---integer)

## OVER

Push a copy of the second element of the stack.

## PRINT

Pop and print an [integer](definitions.md#integer-types) from the stack to the console.
