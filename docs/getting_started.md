# Getting Started

For now, the language only works with Linux using x86_64 architecture. Windows users can use the language with [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install).

## How does Torth work?

- Compiler [torth.torth](../torth.torth) generates Assembly from the Torth code
- Assembly is compiled with NASM into an object file
- Object file is linked to a statically linked 64-bit ELF-executable with LD
- The resulting executable does not have any external dependencies

## Install requirements

The following requirements can probably be installed via your distro's package manager, for example, [APT](https://manpages.ubuntu.com/manpages/xenial/man8/apt.8.html) for Ubuntu and Debian.

- NASM
- LD (**binutils** package in APT)
- Git (For cloning the repository, not required)

## Compile the compiler

The Torth compiler does not ship with the repository. Instead, you must compile it from its [Assembly version](../bootstrap/torth.asm).

1. Clone the [Torth](https://github.com/CyberPaddy/torth) repository from GitHub
1. Compile the Assembly source code with NASM using the `make` command

```sh
$ git clone https://github.com/CyberPaddy/torth.git
$ cd torth/
$ make
$ ./torth --help
```

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

Coding in any language could be pretty painful without syntax highlighting for the particular editor you are using. Torth currently only supports syntax highlighting for [VIM](syntax_highlighting.md#vim) and [VSCode](syntax_highlighting.md#visual-studio-code). There is also a really barebones and outdated [torth-mode](./../editor/emacs/torth-mode.el) for Emacs.

If you want support for a particular editor, please create a [feature request issue](https://github.com/CyberPaddy/torth/issues/new/choose). Contributions are also appreciated, so feel free to create a syntax highlighting configuration to an editor to the [editor](../editor/) folder and hit me with a pull request!

## Check examples

The [examples](../examples/) folder contains some example programs that show how the language can be used. For example, there are [FizzBuzz](../examples/fizzbuzz.torth) and [Fibonacci number sequence](../examples/fibonacci.torth) as well as implementations of some [Project Euler problems](../examples/euler/). The [torth.torth](./../torth.torth) compiler itself is also written in Torth, so it could also be used as an example.

## Read documentation

- [Intrinsics](intrinsics.md)
- [Keywords](keywords.md)
- [Types](types.md)
- [Control flow statements](control_flow.md)
- [Syntax highlighting](syntax_highlighting.md)
