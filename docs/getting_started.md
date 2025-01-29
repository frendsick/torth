# Getting Started

For now, the language only works with Linux using x86_64 architecture. Windows users can use the language with [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install).

## How does Torth work?

- Compiler [torth.torth](../torth.torth) generates Assembly from the Torth code
- Assembly is compiled with NASM into an object file
- Object file is linked to a statically linked 64-bit ELF-executable with LD
- The resulting executable does not have any external dependencies

## Requirements

The following requirements can be installed via your Linux distro's package manager.

- [NASM](https://www.nasm.us/)
- [LD](https://linux.die.net/man/1/ld) (_binutils_ package in APT)

## Installation

Install the Torth compiler and the `std.torth` library from the [releases](https://github.com/frendsick/torth/releases/latest) and put them in the same folder. Alternatively, you can create a `lib` folder inside the folder that contains the `torth` compiler and store the libraries there.

## Compile your first program

1. Create a file with **.torth** extension. Let's do _hello.torth_.
1. Copy the code from [Hello World](../examples/hello_world.torth) example to your _hello.torth_ file.
1. Compile the program: `./torth -v hello.torth`
1. Run the compiled executable: `./hello`

```sh
$ cat hello.torth
include "std"
function main :
  "Hello, World!\n" puts
end
$ ./torth hello.torth
$ ./hello
Hello, World!
```

## Apply syntax highlighting

Coding in any language could be painful without syntax highlighting for the particular editor you are using. Torth currently only supports syntax highlighting for [VIM](syntax_highlighting.md#vim) and [VSCode](syntax_highlighting.md#visual-studio-code). There is also a really barebones and outdated [torth-mode](./../editor/emacs/torth-mode.el) for Emacs.

## Check examples

The [examples](../examples/) folder contains some example programs that show how the language can be used. For example, there are [FizzBuzz](../examples/fizzbuzz.torth) and [Fibonacci number sequence](../examples/fibonacci.torth) as well as implementations of some [Project Euler problems](../examples/euler/). The [torth.torth](./../torth.torth) compiler itself is also written in Torth.

## Read documentation

- [Intrinsics](intrinsics.md)
- [Keywords](keywords.md)
- [Types](types.md)
- [Control flow statements](control_flow.md)
- [Syntax highlighting](syntax_highlighting.md)
