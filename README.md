# Torth

Stack based programming language inspired by [Porth](https://gitlab.com/tsoding/porth) that uses [Reverse Polish notation](./docs/definitions.md#reverse-polish-notation).

Torth is planned to be

- [x] Compiled
- [x] Statically typed
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)
- [x] [Turing complete](examples/rule110.torth)
- [ ] Self-hosted

## Documentation

- [Getting started](./docs/getting_started.md)
- [Types](./docs/types.md)
- [Keywords](./docs/keywords.md)
- [Intrinsics](./docs/intrinsics.md)
- [Control flow statements](./docs/control_flow.md)

## Usage

```pascal
$ cat hello.torth
include "std"
function main : "Hello, World!\n" puts end
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

## Examples

More examples are found from the [examples](./examples/)-folder.

### Hello World

```pascal
include "std"
function Main :
    "Hello, World!\n" puts
end
```

### FizzBuzz

```pascal
include "std"
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

function Main :
    30  // limit
    FizzBuzz

    "Sum of all numbers not divisible by 3 or 5: " OutputRow
    drop  // Sum
end
```
