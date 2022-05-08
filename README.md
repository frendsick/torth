# Torth

It's like [Porth](https://gitlab.com/tsoding/porth) but written by a first-time programming language developer.

Torth is planned to be

- [x] Compiled
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)

## Requirements

- Python3.6 or newer
- NASM
- LD

## Usage

```console
$ cat hello.torth
"Hello, World!" puts
$ ./torth.py --run hello.torth
Hello, World!
```

## Examples

Hello World

```pascal
"Hello, World!" puts
```

Program that does different arithmetic operations and prints their output

```pascal
420 917 + PRINT_INT // Prints 1337 to stdout
9001 7664 - .       // . is the same as PRINT_INT
13379               // Code alignment does not matter
10                  // Division rounds down
        /           // 13379 / 10 => 1337
    PrInT_InT       // Keywords are case insensitive
```

FizzBuzz which also counts the sum of the numbers not divisible by 3 or 5

```pascal
// Args: STR, INT
// Returns: None
MACRO OutputRow
    print dup print_int
END

// Args: Row, Total
// Returns: Row, Total
MACRO AddTotal
    dup rot + swap
END

0 // The sum of numbers not divisible by 3 or 5
1 WHILE 30 >= DO
    IF 15 % 0 == DO
        "FizzBuzz  " OutputRow
    ELIF 3 % 0 == DO
        "Fizz      " OutputRow
    ELIF 5 % 0 == DO
        "Buzz      " OutputRow
    ELSE
        // Add current number to the sum of numbers not divisible by 3 or 5
        AddTotal
    ENDIF
    1 +
DONE drop // Drop the counter from the stack

"Sum of all numbers not divisible by 3 or 5: " OutputRow
```

## Documentation

- [Keywords](./docs/keywords.md)
