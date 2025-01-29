# Intrinsics

Intrinsics are built-in functions that generate static assembly output. The key difference between a [keyword](keywords.md) and an intrinsic is that the behavior of a keyword is dependent on other words in the program. In contrast, an intrinsic will always generate the same assembly output regardless of the context in which it is used.

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

The first parameter decides the number of places to shift; the second parameter is the bit-shifted value.

Different bit shift intrinsics:

- `SHL` Bit shift left
- `SHR` Bit shift right

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

Push the command line argument count `argc` to the stack.

## ARGV

Push the pointer to the command line argument array `*argv[]` to the stack.

## DROP

Remove the top element from the stack.

`a b -> b`

## DUP

Duplicate the top element of the stack.

`a b -> a a b`

## ENVP

Push the environment pointer `*envp[]` to the stack.

## EXEC

Pop and execute a [function pointer](types#fn---function-pointer) from the stack.

**Example**

`2 add_one& exec` -> `3`

Where the `add_one` function is defined as follows:

```
function add_one int -> int :
    1 +
end
```

## LOAD

Load a value from a memory location pointed by a [pointer](types.md#ptr---pointer).

### LOAD Variants

There are four different `LOAD` intrinsic variants:

- `LOAD_BYTE` (8-bit)
- `LOAD_WORD` (16-bit)
- `LOAD_DWORD` (32-bit)
- `LOAD_QWORD` (64-bit)

For example, to load a value of type [INT](types.md#int---integer) (64-bit) from a memory location to the stack, you should use the `LOAD_QWORD` intrinsic.

`pointer_to_int load_qword`

You can also use the _type.load_ functions from the [std-library](../lib/std.torth) which also explicitly cast the loaded value to the corresponding [type](types.md). There is a typed load function for every [built-in type](types.md#built-in-types), for example `int.load`.

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

Rotate the top three items on the stack so that the third element moves to the top and the other two move one spot deeper in the stack.

`a b c -> c a b`

## STORE

Store a value to a memory location pointed by a [pointer](types.md#ptr---pointer).

### STORE Variants

There are four different `STORE` intrinsic variants:

- `STORE_BYTE` (8-bit)
- `STORE_WORD` (16-bit)
- `STORE_DWORD` (32-bit)
- `STORE_QWORD` (64-bit)

For example, to store [INT](types.md#int---integer) (64-bit) to a memory location, you should use the `STORE_QWORD` intrinsic.

`42 pointer_to_int store_qword`

You can also use the _type.store_ functions from the [std-library](../lib/std.torth), which also checks if the value in the stack that is to be stored is of the correct [type](types.md). There is a typed store function for every [built-in type](types.md#built-in-types), for example `int.store`.

## SWAP

Swap the top two elements in the stack.

`a b -> b a`

## SYSCALL

`SYSCALL`-intrinsic variants call a Linux syscall. Syscalls require different amounts of arguments from 0 to 6. Different variants are named `SYSCALL0` - `SYSCALL6` based on the number of arguments. The first argument is the number of the syscall. See [x86_64 syscall table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#x86_64-64_bit)

The different syscall constants can be found in the [sys](../lib/sys.torth) library. Naming convention (case sensitive): `SYS_<syscall>`, for example, `SYS_write`.

Example of how to print "Hello, World!" to `stdout` without any library dependencies using the [write](https://man7.org/linux/man-pages/man2/write.2.html) syscall:

`14 "Hello, World!\n" 1 1 syscall3`
