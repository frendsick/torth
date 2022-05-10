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
function Main -- -> ret :
    "Hello, World!" puts
end
```

FizzBuzz which also counts the sum of the numbers not divisible by 3 or 5

```pascal
function OutputRow -- str_buf* str_len number -> number :
    print dup print_int
end

function AddTotal -- row total -> row total :
    dup rot + swap
end

function FizzBuzz -- index sum limit -> sum :
    // WHILE index <= limit
    WHILE 3 get_nth over <= DO
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
    DONE drop swap drop // Drop the counter and limit from the stack
end

function Main -- -> int :
    30  // limit
    0   // sum
    1   // index

    FizzBuzz

    "Sum of all numbers not divisible by 3 or 5: " OutputRow drop
    0 // return 0
end
```

## Documentation

- [Keywords](./docs/keywords.md)
