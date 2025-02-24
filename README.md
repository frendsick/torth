# Torth

Stack-based programming language inspired by [Porth](https://gitlab.com/tsoding/porth).

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

```sh
$ cat hello.torth
include "std"
function main :
  "Hello, World!\n" puts
end
$ ./torth -r hello.torth
Hello, World!
$ ./torth --help
Usage: ./torth [-h] [--out FILE] [-r] [-s] [-v] code_file

Torth compiler

Positional arguments:
  code_file             Input file

Options:
  -h                    Show this help message and exit
  --out FILE            Output file
  -r                    Run program after compilation
  -s                    Save files generated during compilation
  -v                    Output compilation steps
```

## Examples

More examples are found in the [examples](./examples/) folder.

### [Hello World](./examples/hello_world.torth)

```pascal
include "std"

function main :
    "Hello, World!\n" puts
end
```

### [Fibonacci](./examples/fibonacci.torth)

```pascal
include "std"

function Fib number:int -> int :
  if number 1 <= do
    number return
  endif

  // Fib(number-1) + Fib(number-2)
  number 1 - Fib
  number 2 - Fib +
end

function main :
  20 Fib putu // Prints: 4181
end
```

### [FizzBuzz](./examples/fizzbuzz.torth)

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

// Returns the sum of numbers not divisible by 3 or 5
function FizzBuzz limit:int -> int :
    // Push the initial values to stack
    0   // sum
    1   // index

    // Save two topmost values from the stack to variables
    // => The TAKE keyword also removes the values from the stack
    // => The PEEK keyword would instead save the values without removing them from the stack
    take index sum in

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
    sum // Return sum
end

// Program execution starts from the `main` function
function main :
    // Call FizzBuzz with one integer parameter
    // FizzBuzz(limit=30)
    30 FizzBuzz

    // Save the return value to a variable called sum and print it with text
    take sum in
    "Sum of all numbers not divisible by 3 or 5: " puts
    sum putu "\n" puts
end
```
