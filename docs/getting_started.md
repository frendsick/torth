# Getting Started

For now, the language only works with Linux using x86_64 architecture. Windows-users can use the language with [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install).

## How does Torth work?

- Compiler [torth.torth](../torth.torth) generates Assembly from the Torth code
- Assembly is compiled with NASM into object file
- Object file is linked to a statically linked 64-bit ELF-executable with LD
- The resulting executable does not have any external dependencies

## Install requirements

The following requirements can probably be installed via your distro's package manager, for example [APT](https://manpages.ubuntu.com/manpages/xenial/man8/apt.8.html) for Ubuntu and Debian.

- NASM
- LD (**binutils** package in APT)
- Git (For cloning the repository, not required)

## Compile your first program

1. Download **torth** binary from [Releases](https://github.com/CyberPaddy/torth/releases/latest)
2. Create a file with .torth extension. Let's do _hello.torth_.
3. Include the code from [Hello World](../examples/hello_world.torth) example.
4. Compile the program: `./torth hello.torth`
5. Run the program: `./hello`

## Apply syntax highlighting

Coding in any language could be pretty painful without syntax highlighting for the particular editor you are using. Torth currently only supports syntax highlighting for [VIM](syntax_highlighting.md#vim) and [VSCode](syntax_highlighting.md#visual-studio-code). There is also a really barebones and outdated [torth-mode](./../editor/emacs/torth-mode.el) for Emacs.

If you want a support for a particular editor, please create a [feature request issue](https://github.com/CyberPaddy/torth/issues/new/choose). Contributions are also appreciated so feel free to create syntax highlighting configuration to an editor to the [editor](../editor/) folder and hit me with a pull request!

## Read documentation

- [Intrinsics](intrinsics.md)
- [Keywords](keywords.md)
- [Types](types.md)
- [Control flow statements](control_flow.md)
- [Syntax highlighting](syntax_highlighting.md)

## Check examples

The [examples](../examples/) folder contains some example programs that show how the language can be used. For example, there are [FizzBuzz](../examples/fizzbuzz.torth) and [Fibonacci number sequence](../examples/fibonacci.torth) as well as implementations of some [Project Euler problems](../examples/euler/). The [torth.torth](./../torth.torth) compiler itself is also written in Torth so it could also be used as an example.
