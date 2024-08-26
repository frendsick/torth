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
- [RETURN](#RETURN)
- [WHILE](#WHILE)

## BREAK

BREAK is an unconditional jump to the operation after [DONE](#done) of the current loop.

- [How to use BREAK?](control_flow.md#break-statement)

## CAST

The CAST keyword is used to cast any type to another. The keyword does not generate any assembly code and thus does not affect the effectiveness of the resulting binary.

## CONST

Constants are named literal values that cannot be modified. The constant name can be used in code to push the constant's value to the stack.

### Syntax

```pascal
CONST <name> <value> END
```

### Examples

```pascal
const DATABASE "/dev/null" end
const MAX_USERS 1337 end
```

## CONTINUE

CONTINUE is an unconditional jump to the current loop's [WHILE](#while).

- [How to use CONTINUE?](control_flow.md#continue-statement)

## DO

DO is a conditional jump to the operation after the next [ELIF](#elif), [ELSE](#else), [ENDIF](#endif), or [DONE](#done).

The conditional jump will occur if the condition does not match because if it does, the block of code should be executed.

With [IF](#if) and [ELIF](#elif) statements, DO is a conditional jump to the operation after the next [ELIF](#elif), [ELSE](#else) or [ENDIF](#endif) keywords.

In [WHILE](#while) loop, DO is a conditional jump to operation after [DONE](#done).

See also:

- [IF Blocks](control_flow.md#if-blocks)
- [WHILE Loops](control_flow.md#while-loops)

## DONE

DONE is an unconditional jump to the [WHILE](#while) keyword. The loop's condition is always evaluated by the [DO](#do) keyword after [WHILE](#while), which is also a conditional jump to the operation after the DONE keyword.

See also:

- [WHILE Loops](control_flow.md#while-loops)

## ELIF

ELIF unconditionally jumps to the operation after [ENDIF](#endif). It's also a keyword for [DO](#do) to conditionally jump over.

ELIF is an unconditional jump to the operation after [ENDIF](#endif) because the keyword is only reached if the previous [IF](#if) or ELIF block's condition is true. [DO](#do) keyword is a conditional jump to the operation after ELIF if the condition is false.

See also:

- [IF Blocks](control_flow.md#if-block)

## ELSE

ELSE unconditionally jumps to the operation after [ENDIF](#endif). It's also a keyword for [DO](#do) to conditionally jump over.

ELSE is an unconditional jump to the operation after [ENDIF](#endif) because the keyword is only reached if the previous [IF](#if) or [ELIF](#elif) block's condition was true. [DO](#do) keyword is a conditional jump to the operation after ELSE if the condition is false.

See also:

- [IF Blocks](control_flow.md#if-block)

## ENDIF

ENDIF is a keyword for [DO](#do), [ELIF](#elif), or [ELSE](#else) keywords to jump over.

See also:

- [IF Blocks](control_flow.md#if-block)

## ENUM

Enumerations in Torth enable generating named running integer values with a certain positive offset between each integer. Names defined inside the ENUM block can be used as tokens in the code, just like [constants](#CONST). The ENUM block's name will also be a constant with the value of `offset * items_count`.

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
  item2 item5 + putu      // 1 + 3 = 4
  item3 item4 + putu      // 2 + 0 = 2
  "\n" puts               // Output: 42

  item6 putu              // 6
  offset_by_three putu    // 9 (offset * item_count)
  "\n" puts               // Output: 69
end
```

## FUNCTION

Functions are defined using the FUNCTION keyword. Functions are pieces of code that can be called from wherever inside the program by using its name as a token. When called, the function's name is replaced with the contents of the function (**function_body** in the [Function syntax](#function-syntax) section) during compilation. Defined functions are case-sensitive tokens, unlike most other keywords in Torth.

The **main** function (case-sensitive) is mandatory in every Torth program. It is the function from which the execution starts. The main function cannot take any parameters, and it either returns nothing or one [INT](types.md#int---integer), which will become the program's return value. The default return value is 0 (success) if nothing is returned.

Functions do not take parameters but instead use the current stack. The required topmost items in the stack before and after the function execution are defined in the function declaration (**argument_types** and **return_types** in the following [Function syntax](#function-syntax) section). The compiler verifies at compile time if the topmost types in the stack match with the function signature before and after its execution. If there are more items in the return types than argument types, then the compiler will assume that there should be more elements in the stack after the execution than before calling the function and vice versa.

If the function does not return anything, it can be declared without the `->` token (See [Function syntax](#function-syntax)).

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
  puts // Prints name
  if dup 18 > do
    False " you are not an adult"
  else
    True  " you are an adult"
  endif puts // Prints
end

function main :
  42 "frendsick" is_adult
  "Return value: " puts putu "\n" puts // Output: 40
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
  5 multiply_by_two MultiplyByFour putu "\n" puts // Output: 40
end
```

```pascal
// Non-zero exit code example
include "std"
function main -> int :
  42 dup
  "This program will return with exit code " puts putu "\n" puts
end
```

## IF

IF is just a keyword that starts an [IF block](control_flow.md#if-blocks). IF-block ends to [ENDIF](#ENDIF).

## INCLUDE

With the INCLUDE keyword, you can include code from another file. The INCLUDE statement consists of the keyword INCLUDE and the file to be imported in double quotes ("). The file name should be either its absolute file path or the relative path compared to the compiler file [torth.torth](../torth.torth). The file can also refer to a relative path from the compiler file with any of the entries in [PATH](definitions.md#path) as the parent directory.

Note: A file will only be included once, even if it is included by multiple different included files. Thus, it is safe and preferable to include every needed file in each of the different files.

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

## RETURN

Return from current [FUNCTION](#function).

[How to use RETURN keyword?](control_flow.md#return-keyword)

## WHILE

WHILE is a keyword to jump to for [DONE](#done).

[How to use WHILE Loops?](control_flow.md#while-loops)
