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
usage: torth.py [-h] [-o FILE] [-d] [-g] [-r] [-s] code_file

Compile Torth code

positional arguments:
  code_file            Input file

optional arguments:
  -h, --help           show this help message and exit
  -o FILE, --out FILE  Output file
  -d, --debug          Do not strip the resulting binary
  -g, --graph          Generate Graphviz graph from the program's control flow
  -r, --run            Run program after compilation
  -s, --save-asm       Save assembly file named after code_file with .asm extension
```

## Documentation

- [Intrinsics](./docs/intrinsics.md)
- [Keywords](./docs/keywords.md)
- [Types](./docs/types.md)

## Examples

More examples are found from the [examples](./examples/)-folder.

### Hello World

```pascal
function Main -> :
    "Hello, World!\n" puts
end
```

### FizzBuzz

```pascal
include "lib/std.torth"
function OutputRow str int -> int :
    puts dup print "\n" puts
end

function AddTotal int int -> int int :
    dup rot + swap
end

function FizzBuzz int -> int :
    0   // sum
    1   // index
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
    FizzBuzz

    "Sum of all numbers not divisible by 3 or 5: " OutputRow
    drop  // Sum
end
```
