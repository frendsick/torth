# Getting Started

For now, the language only works with Linux using x86_64 architecture. Windows-users can use the language with [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install).

## How does Torth work?

- Compiler [torth.py](../torth.py) generates Assembly from the Torth code
- Assembly is compiled with NASM to an object file
- Object file is linked to a statically linked 64-bit ELF-executable with LD
- The resulting executable does not have any external dependencies

## Install requirements

The following requirements can probably be installed via your distro's package manager.

- Python3.6 or newer
- NASM
- LD
- Graphviz (Only required for creating Graphviz graphs with **-g** argument)

## Compile your first program

1. Clone the repository `git clone https://github.com/CyberPaddy/torth`
2. Change directory to the cloned repository `cd torth`
3. Create a file with .torth extension. Let's do _hello.torth_.
4. Include the code from [Hello World](../examples/hello_world.torth) example.
5. Compile the program: `./torth.py hello.torth`
6. Run the program: `./hello.bin`

## Read documentation

- [Intrinsics](./docs/intrinsics.md)
- [Keywords](./docs/keywords.md)
- [Types](./docs/types.md)
- [Control flow statements](./docs/control_flow.md)

## Check examples

The [examples](../examples/) folder contains some example programs that show how the language can be used. For example, there are [FizzBuzz](../examples/fizzbuzz.torth) and [Fibonacci number sequence](../examples/fibonacci.torth) as well as implementations of some [Project Euler problems](../examples/euler/).
