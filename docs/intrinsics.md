# Intrinsics

Intrinsics are built-in functions that generate static assembly output. The key difference between a [keyword](keywords.md) and an intrinsic is that the behavior of a keyword is dependent on other words in the program, whereas an intrinsic will always generate the same assembly output regardless of the context in which it is used.

## List of Intrinsics

- [AND](#AND)
- [ARGC](#ARGC)
- [ARGV](#ARGV)
- [DIV](#Calculations)
- [DROP](#DROP)
- [DUP](#DUP)
- [ENVP](#ENVP)
- [EXEC](#EXEC)
- [EQ](#Comparisons)
- [GE](#Comparisons)
- [GT](#Comparisons)
- [LE](#Comparisons)
- [LOAD_BYTE](#LOAD)
- [LOAD_WORD](#LOAD)
- [LOAD_DWORD](#LOAD)
- [LOAD_QWORD](#LOAD)
- [LT](#Comparisons)
- [MINUS](#Calculations)
- [MOD](#Calculations)
- [MUL](#Calculations)
- [NE](#Comparisons)
- [OR](#OR)
- [OVER](#OVER)
- [PLUS](#Calculations)
- [ROT](#ROT)
- [SHL](#bit-shifts)
- [SHR](#bit-shifts)
- [STORE_BYTE](#STORE)
- [STORE_WORD](#STORE)
- [STORE_DWORD](#STORE)
- [STORE_QWORD](#STORE)
- [SWAP](#SWAP)
- [SYSCALL0](#SYSCALL)
- [SYSCALL1](#SYSCALL)
- [SYSCALL2](#SYSCALL)
- [SYSCALL3](#SYSCALL)
- [SYSCALL4](#SYSCALL)
- [SYSCALL5](#SYSCALL)
- [SYSCALL6](#SYSCALL)

## Calculations

Perform a calculation operation for two [integers](definitions.md#integer-types).

Different calculation intrinsics:

- `PLUS` | `+`
- `MINUS` | `-`
- `MUL` | `*`
- `DIV` | `/`
- `MOD` | `%`

**Examples**

- `10 3 +` -> `13`
- `10 3 -` -> `7`
- `10 3 *` -> `30`
- `10 3 /` -> `3`
- `10 3 %` -> `1`

## Comparisons

Perform a certain comparison operation to two [integers](definitions.md#integer-types).

Different comparison intrinsics:

- `EQ` | `==`
- `GE` | `>=`
- `GT` | `>`
- `LE` | `<=`
- `LT` | `<`
- `NE` | `!=`

**Examples**

- `10 3 ==` -> `false`
- `10 3 >=` -> `true`
- `10 3 >` -> `true`
- `10 3 <=` -> `false`
- `10 3 <` -> `false`
- `10 3 !=` -> `true`

## Bit shifts

A bit shift moves each digit left or right in the binary representation of an [integer](definitions.md#integer-types).

Different bit shift intrinsics:

- `SHL`: Bit shift left
- `SHR`: Bit shift right

**Examples**

- `16 2 shl` -> `64`
- `16 2 shr` -> `4`

## AND

Perform bitwise AND for two [integers](definitions.md#integer-types).

**Examples**

- `10 3 and` -> `2`
- `16 5 and` -> `0`
- `15 15 and` -> `15`

## ARGC

Push the command line argument count to the stack.

## ARGV

Push the pointer to the command line argument array to the stack.

## DROP

Remove the top element from the stack.

`a b -> b`

## DUP

Duplicate the top element of the stack.

`a b -> a a b`

## ENVP

Push the environment pointer to the stack.

## EXEC

Pop and execute a [function pointer](types#fn---function-pointer) from the stack.

## LOAD

Load a value from a memory location pointer by a [PTR](types.md#ptr---pointer). LOAD-intrinsics push a value pointed by a [pointer-like](types.md#ptr---pointer) type to the stack.

1. Pop a [PTR](types.md#ptr---pointer) type value from the stack
2. Push the value pointed by the popped pointer to the stack

### LOAD Variants

There are four different LOAD intrinsic variants:

- LOAD_BYTE (8-bit)
- LOAD_WORD (16-bit)
- LOAD_DWORD (32-bit)
- LOAD_QWORD (64-bit)

For example, to load a value of type [INT](types.md#int---integer) (64-bit) from a memory location to the stack, you should use the LOAD_QWORD intrinsic. Also, it is preferred to use the _type.load_ functions from the [std-library](../lib/std.torth) which also explicitly cast the loaded value to the corresponding [type](types.md). There is a typed load function for every [built-in type](types.md#built-in-types), for example `int.load`.

## OR

Perform bitwise OR for two [integers](definitions.md#integer-types).

**Examples**

- `10 3 or` -> `11`
- `16 5 or` -> `21`
- `15 15 or` -> `15`

## OVER

Push a copy of the second element of the stack.

`a b -> b a b`

## ROT

Rotate the top three items on the stack so that the third element moves to the top and the other two moves one spot deeper in the stack.

`a b c -> c a b`

## STORE

A [PTR](types.md#ptr---pointer) stores a value to a memory location pointer. STORE-intrinsics pops two values from the stack. The second item of the stack is stored in the memory address pointed by the first.

- The top element should be of type [PTR](types.md#ptr---pointer)
- The second element is stored at the address pointed by the pointer

### STORE Variants

There are four different STORE intrinsic variants:

- STORE_BYTE (8-bit)
- STORE_WORD (16-bit)
- STORE_DWORD (32-bit)
- STORE_QWORD (64-bit)

For example, to store [INT](types.md#int---integer) (64-bit) to a memory location, you should use the STORE_QWORD intrinsic. Also, it is preferred to use the _type.store_ functions from the [std-library](../lib/std.torth), which also checks if the value in the stack that is to be stored is of the correct [type](types.md). There is a typed store function for every [built-in type](types.md#built-in-types), for example `int.store`.

## SWAP

Swap the top two elements in the stack.

`a b -> b a`

## SYSCALL

SYSCALL-intrinsic variants call a Linux syscall. Syscalls require different amounts of arguments from 0 to 6. Different variants are named SYSCALL0 - SYSCALL6 by the amount of arguments. The first argument should be an [integer](definitions.md#integer-types).

1. Pop the top element and the required number of arguments from the stack
2. Call the syscall which matches the first popped element

The different syscall constants can be found from lib/sys.torth. Naming convention (case sensitive): SYS\_<syscall>. For example, **SYS_write**.
