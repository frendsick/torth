# Torth

Stack based programming language inspired by [Porth](https://gitlab.com/tsoding/porth) that uses [Reverse Polish notation](./docs/definitions.md#reverse-polish-notation).

Torth is planned to be

- [x] Compiled
- [x] Statically typed
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)
- [x] [Turing complete](examples/rule110.torth)
- [x] Self-hosted

## Documentation

- [Getting started](./docs/getting_started.md)
- [Intrinsics](./docs/intrinsics.md)
- [Keywords](./docs/keywords.md)
- [Types](./docs/types.md)
- [Control flow statements](./docs/control_flow.md)
- [Syntax highlighting](./docs/syntax_highlighting.md)

## Usage

```pascal
$ cat hello.torth
include "std"
function main : "Hello, World!\n" puts end
$ ./torth.py --run hello.torth
Hello, World!
$ ./torth.py --help
usage: torth.py [-h] [-o FILE] [-p DIRS] [-r] [-s] [-v] code_file

Compile Torth code

positional arguments:
  code_file             Input file

optional arguments:
  -h, --help            show this help message and exit
  -o FILE, --out FILE   Output file
  -p DIRS, --path DIRS  Comma separated list of directories to be added to PATH in addition of the default "lib"
  -r, --run             Run program after compilation
  -s, --save-asm        Save assembly file named after code_file with .asm extension
  -v, --verbose         Output compilation steps
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
// === FIZZBUZZ ===
// Print integers 1 to N with some exceptions:
// => Print “Fizz” if an integer is divisible by 3
// => Print “Buzz” if an integer is divisible by 5
// => Print “FizzBuzz” if an integer is divisible by both 3 and 5

// The standard library implements common functions, for example:
// puts => Output string
// %    => Modulo-operator
include "std"

// Program execution starts from MAIN function (case-insensitive)
function main :
    // Push the initial values to stack
    0   // sum
    1   // index
    30  // limit

    // Save values from the stack to variables, topmost value first
    // => TAKE keyword also removes the values from the stack
    // => PEEK keyword would instead save the values without removing them from the stack
    take
        limit
        index
        sum
    in

    // Loop while index <= limit
    WHILE index limit <= DO

        // Newlines inside IF condition are just for readability
        // => The whole program could be in one line
        IF
            index 3 % 0 ==
            index 5 % 0 ==
            &&
        DO
            "FizzBuzz\n" puts
        ELIF index 3 % 0 == DO
            "Fizz\n" puts
        ELIF index 5 % 0 == DO
            "Buzz\n" puts
        ELSE
            // Print the current index
            index putu "\n" puts

            // Add index to sum
            sum index + sum =
        ENDIF

        // Increment loop's index
        index 1 + index =
    DONE

    "Sum of all numbers not divisible by 3 or 5: " puts
    sum putu "\n" puts
end
```
