# Torth

It's like [Porth](https://gitlab.com/tsoding/porth) but written by a first-time programming language developer.

Torth is planned to be
- [x] Compiled
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)

## Usage

```console
$ cat hello.torth
"Hello, World!" puts
$ ./torth.py hello.torth
Hello, World!
```

## Examples

Hello World

```pascal
"Hello, World!" puts
```

Program that adds two numbers and prints their sum

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
0 // The sum of numbers not divisible by 3 or 5
1 // The counter for WHILE loop

WHILE dup 30 >= DO
    IF dup 15 % 0 == DO
        "FizzBuzz  " print print_int
    ELIF dup 3 % 0 == DO
        "Fizz      " print print_int
    ELIF dup 5 % 0 == DO
        "Buzz      " print print_int
    ELSE
        // Add current number to the sum of numbers not divisible by 3 or 5
        dup rot + swap
    ENDIF
    1 +
END drop // Drop the counter from the stack

"Sum of all numbers not divisible by 3 or 5: " print print_int
```