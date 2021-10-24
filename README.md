# Torth

It's like [Porth](https://gitlab.com/tsoding/porth) but written by a first-time programming language developer.

Torth is planned to be
- [x] Compiled
- [x] Native (Linux x86_64)
- [x] Stack-based (just like Porth)

## Examples

Hello World

```pascal
"Hello, World!" print
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

## Usage

```console
$ cat arithmetics.torth
420 917 + PRINT_INT // Prints 1337 to stdout
9001 7664 - .       // . is the same as PRINT_INT
13379               // Code alignment does not matter
10                  // Division rounds down
        /           // 13379 / 10 => 1337
    PrInT_InT       // Keywords are case insensitive
$ ./torth.py add_numbers.torth
1337
1337
1337
```
