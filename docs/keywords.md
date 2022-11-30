# Keywords

This is the documentation for different keywords available in the Torth language.

- [BREAK](#BREAK)
- [CAST](#CAST)
- [CONST](#CONST)
- [CONTINUE](#CONTINUE)
- [DO](#DO)
- [DONE](#DONE)
- [ELIF](#ELIF)
- [ELSE](#ELSE)
- [ENDIF](#ENDIF)
- [ENUM](#ENUM)
- [FUNCTION](#FUNCTION)
- [IF](#IF)
- [INCLUDE](#INCLUDE)
- [MEMORY](#MEMORY)
- [RETURN](#RETURN)
- [WHILE](#WHILE)

## BREAK

BREAK is unconditional jump to the operation after [DONE](#done) of the current loop.

- [How to use BREAK?](control_flow.md#break-statement)

## CAST

CAST keyword is used to cast any type to another. The keyword does not generate any assembly code and thus does not affect the effectiveness of the resulting binary.

## CONST

Constants are named integer values that cannot be modified. The constant name can be used in code to push the constant's integer value to the stack. Constants can also be used in [MEMORY](#MEMORY) declarations when defining the size of the memory. However, constants cannot be used in defining other constants at least for now.

### Syntax

```pascal
// Constant declarations should be in one line
CONST <name> <integer> END
```

### Examples

```pascal
include "std"
const ptr.size 8 end
memory dst ptr.size end
memory src ptr.size end

function main :
  1337 src int.store          // Store 1337 to src
  9001 dst int.store          // Store 9001 to dst
  src int.load dst int.store  // Copy the value from src to dst
  src int.load print          // Print the value 1337 from src
  dst int.load print          // Print the value 1337 from dst
end  // Expected output: 13371337
```

## CONTINUE

CONTINUE is unconditional jump to the current loop's [WHILE](#while).

- [How to use CONTINUE?](control_flow.md#continue-statement)

## DO

DO is a conditional jump to the operation after next [ELIF](#elif), [ELSE](#else), [ENDIF](#endif) or [DONE](#done).

The conditional jump will occur if the condition does not match because if it does the block of code should be executed.

With [IF](#if) and [ELIF](#elif) statements, DO is a conditional jump to the operation after the next [ELIF](#elif), [ELSE](#else) or [ENDIF](#endif) keywords.

In [WHILE](#while) loop, DO is a conditional jump to operation after [DONE](#done).

See also:

- [IF Blocks](control_flow.md#if-blocks)
- [WHILE Loops](control_flow.md#while-loops)

## DONE

DONE is an unconditional jump to [WHILE](#while) keyword. The loop's condition is always evaluated by the [DO](#do) keyword after [WHILE](#while) which is also a conditional jump to the operation after the DONE keyword.

See also:

- [WHILE Loops](control_flow.md#while-loops)

## ELIF

ELIF is an unconditional jump to the operation after [ENDIF](#endif). It's also a keyword for [DO](#do) to coditionally jump over.

ELIF is a unconditional jump to the operation after [ENDIF](#endif) because the keyword is only reached if the previous [IF](#if) or ELIF block's condition was true. [DO](#do) keyword is a conditional jump to the operation after ELIF if the condition is false.

See also:

- [IF Blocks](control_flow.md#if-block)

## ELSE

ELSE is an unconditional jump to the operation after [ENDIF](#endif). It's also a keyword for [DO](#do) to coditionally jump over.

ELSE is a unconditional jump to the operation after [ENDIF](#endif) because the keyword is only reached if the previous [IF](#if) or [ELIF](#elif) block's condition was true. [DO](#do) keyword is a conditional jump to the operation after ELSE if the condition is false.

See also:

- [IF Blocks](control_flow.md#if-block)

## ENDIF

ENDIF is a keyword for [DO](#do), [ELIF](#elif), or [ELSE](#else) keywords to jump over.

See also:

- [IF Blocks](control_flow.md#if-block)

## ENUM

Enumerations in Torth enable generating named running integer values with certain positive offset between each integer. Names defined inside ENUM block can be used as tokens in the code just like [constants](#CONST). The ENUM block's name will also be a constant with the value of `offset * items_count`.

See also:

- [CONST](#CONST)

### Syntax

```pascal
ENUM <name> <offset> : item1 item2 END
```

### Examples

```pascal
ENUM offset_by_one 1 : item1 item2 item3 END
ENUM offset_by_three 3 :
  item4 // 0
  item5 // 3
  item6 // 6
        // ...
END

include "std"
function main :
  item2 item5 + print     // 1 + 3 = 4
  item3 item4 + print     // 2 + 0 = 2
  "\n" puts               // Output: 42

  item6 print             // 6
  offset_by_three print   // 9 (offset * item_count)
  "\n" puts               // Output: 69
end
```

## FUNCTION

Functions are defined using FUNCTION keyword. Functions are pieces of code that can be called from wherever inside the program by using its name as token. When called, the function's name is replaced with the contents of the function (**function_body** in the [Function syntax](#function-syntax) section) during compilation. Defined functions are case sensitive tokens unlike most other keywords in Torth.

The **main** function (case sensitive) is mandatory in every Torth program. It is the function from which the execution starts. The main function cannot take any parameters and it either returns nothing or one [INT](types.md#int---integer) which will become the return value of the program. The default return value is 0 (success) if nothing is returned.

Functions do not take parameters but instead use the current stack. The required topmost items in the stack before and after the function execution are defined in the function declaration (**argument_types** and **return_types** in the following [Function syntax](#function-syntax) section). Compiler verifies at compile time if the topmost types in the stack would match with the function signature before and after its execution. If there is more items in the return types than argument types then the compiler will assume that there should be more elements in the stack after the execution than before calling the function and vice versa.

If the function does not return anything it can be declared without the `->` token (See [Function syntax](#function-syntax)).

### Function syntax

```pascal
// Different tokens or words can be on different lines
FUNCTION <name> <argument_types> -> <return_types> : <function_body> END

// Functions without return types can be defined without the '->' token
FUNCTION <name> <argument_types> : <function_body> END
```

### Examples

```pascal
include "std"
// Example with name and age as parameters, name is on top of the stack
// Note: Strings pushes two items to the stack, it's length and pointer to the string buffer
function is_adult str int int -> bool :
  print // Prints name
  if dup 18 > do
    False " you are not an adult"
  else
    True  " you are an adult"
  endif puts // Prints
end

function main :
  42 "CyberPaddy" is_adult
  "Return value: " puts print "\n" puts // Output: 40
end
```

```pascal
INCLUDE "std"
FUNCTION multiply_by_two int -> int : 2 * END

// Functions can be called from within another function
function MultiplyByFour
  int
  ->
  int :
    multiply_by_two
    multiply_by_two
end

function main :
  5 multiply_by_two MultiplyByFour print "\n" puts // Output: 40
end
```

```pascal
// Non-zero exit code example
include "std"
function main -> int :
  42 dup
  "This program will return with exit code " puts print "\n" puts
end
```

## IF

IF is just a keyword which starts an [IF block](control_flow.md#if-blocks). IF-block ends to [ENDIF](#ENDIF).

## INCLUDE

With INCLUDE keyword you can include code from another files. The INCLUDE statement consists of the keyword INCLUDE and the file to be imported in double quotes ("). The file name should be either its absolute file path or the relative path compared to the compiler file [torth.py](../torth.py). The file can also refer to a relative path from compiler file with any of the entries in [PATH](definitions.md#path) as the parent directory.

Note: A file will only be included once even if it is included by multiple different included files. Thus, it is safe and preferrable to include every needed file in each of the different files.

### Syntax

```pascal
// The whole statement has to be in one line
INCLUDE "<file>"
```

### Limitations

There are some limitations in using INCLUDE statements:

- Statement MUST be outside a function
- Statement MUST be in one line

### Examples

```pascal
// Different styles of including the std-library
INCLUDE "std"
INCLUDE "std.torth"
INCLUDE "lib/std"
INCLUDE "lib/std.torth"
INCLUDE "path/to/torth/lib/std.torth"
```

## MEMORY

Named memory locations with certain size can be defined with MEMORY keyword. These are named pointers to a read-write section .bss in the executable. A pointer to a memory can then be pushed to the stack by using the memory's name as a token. Values can then be stored to the memory location with STORE intrinsics and values are loaded from memory to the stack with LOAD intrinsics.

### Syntax

```pascal
// Memory declaration should be in one line
MEMORY <name> <size> END
```

### Examples

```pascal
include "std"
memory leet int.size end  // int.size = 8
memory feet ptr.size end  // ptr.size = 8
function main -> :
  1337 leet int.store
  leet int.load print "\n" puts // Output: 1337

  "pinky\n" feet str.store
  'k' feet ptr.load char.store
  feet str.load puts            // Output: kinky
end
```

## RETURN

Return from current [FUNCTION](#function).

[How to use RETURN keyword?](control_flow.md#return-keyword)

## WHILE

WHILE is a keyword for [DONE](#done) to jump to.

[How to use WHILE Loops?](control_flow.md#while-loops)
