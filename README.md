# Torth

It's like [Porth](https://gitlab.com/tsoding/porth) but written by a first-time programming language developer.

Torth is planned to be

- [x] Compiled
- [x] Statically typed
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)
- [x] [Turing complete](examples/rule110.torth)
- [ ] Self-hosted

## Requirements

- Python3.6 or newer
- NASM
- LD
- Graphviz (Only required for creating Graphviz graphs with **-g** argument)

## Usage

```pascal
$ cat hello.torth
function main -> : "Hello, World!\n" puts end
$ ./torth.py --run hello.torth
Hello, World!
$ ./torth.py --help
usage: torth.py [-h] [--output file] [-r] [-s] [-g] code_file

Compile Torth code

positional arguments:
  code_file             Input file

optional arguments:
  -h, --help            show this help message and exit
  --output file, -o file
                        Output file
  -r, --run             Run program after compilation
  -s, --save-asm        Save assembly file as <code_file>.asm
  -g, --graph           Generate Graphviz graph from the program's control flow
```

## Documentation

- [Keywords](./docs/keywords.md)
- [Type checking](./docs/type_checking.md)

## Examples

Hello World

```pascal
function Main -> :
    "Hello, World!\n" puts
end
```

FizzBuzz which also counts the sum of the numbers not divisible by 3 or 5

```pascal
include "lib/std.torth"
function OutputRow str_buf* str_len number -> int :
    puts dup print "\n" puts
end

function AddTotal row total -> int int :
    dup rot + swap
end

function FizzBuzz index sum limit -> int :
    // WHILE limit >= index
    WHILE dup 4 nth >= DO
        IF dup 15 % 0 == DO
            "FizzBuzz  " OutputRow
        ELIF dup 3 % 0 == DO
            "Fizz      " OutputRow
        ELIF dup 5 % 0 == DO
            "Buzz      " OutputRow
        ELSE
            // Add current number to the sum of numbers not divisible by 3 or 5
            AddTotal
        ENDIF
        1 +
    DONE drop swap drop // Drop the counter and limit from the stack
end

function Main -> :
    30  // limit
    0   // sum
    1   // index

    FizzBuzz

    "Sum of all numbers not divisible by 3 or 5: " OutputRow
end
```
