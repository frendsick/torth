# Torth

It's like [Porth](https://gitlab.com/tsoding/porth) but written by a first-time programming language developer.

Torth is planned to be

- [x] Compiled
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)
- [x] [Turing complete](examples/rule110.torth)
- [ ] Self-hosted

## Requirements

- Python3.6 or newer
- NASM
- LD

## Usage

```pascal
$ cat hello.torth
function main -> : "Hello, World!\n" puts end
$ ./torth.py --run hello.torth
Hello, World!
```

## Examples

Hello World

```pascal
function Main -> :
    "Hello, World!\n" puts
end
```

FizzBuzz which also counts the sum of the numbers not divisible by 3 or 5

```pascal
function OutputRow str_buf* str_len number -> number :
    puts dup print "\n" puts
end

function AddTotal row total -> row total :
    dup rot + swap
end

function FizzBuzz index sum limit -> sum :
    // WHILE limit >= index
    WHILE dup 4 nth >= DO
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

function Main -> :
    30  // limit
    0   // sum
    1   // index

    FizzBuzz

    "Sum of all numbers not divisible by 3 or 5: " OutputRow
end
```

## Documentation

- [Keywords](./docs/keywords.md)
