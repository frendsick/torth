# Types

Torth language is statically typed. Each value pushed to the stack has a type associated with it. Typing tries to ensure that the user only performs operations that are appropriate to the values of specific types.

## Built-in types

The language supports the following built-in types:

- [any](#any)
- [bool](#bool---boolean)
- [char](#char---character)
- [fn](#fn---function-pointer)
- [int](#int---integer)
- [ptr](#ptr---pointer)
- [str](#str---string)

### any

The 'any' type can be used to indicate that a value can be of any type.

**Note**: Please use the 'any' type cautiously because the compiler's type checker cannot check for errors if it is used. The 'any' type should only be used in situations when the function should work for any type in the stack. For example, the 'any' type could be used in a [function](./keywords.md#function) that only modifies the stack state and does not touch the underlying data.

**Note**: The type checker does not know the true type of a value after it has been returned by a function returning 'any'. You could work around that by [casting](#casting) the value to a certain type after it has been returned from the function to ensure the correctness of your program.

#### Examples

Rotate three topmost elements in the stack in the reverse direction as the [rot](intrinsics.md#rot) intrinsic does.

```pascal
// Example: 3 2 1 --> 1 3 2
function reverse_rot any any any -> any any any :
  rot rot
end
```

Print any value as an integer.

```pascal
include "std"
function print_any any :
  cast(int) puti
end
```

### bool - Boolean

Boolean values are True and False. The boolean words are case insensitive.

### char - Character

Characters are defined with single quotes. They are pushed to stack as the integer representation of the character. To print the character, it should be stored in a [string](types.md#str).

### fn - Function pointer

Function pointer is a memory address where a function is located.

Function pointer to a Torth function can be pushed to the stack by appending _&_ (ampersand) character to a function name. For example, to create function pointer to the `add_one` function, use the token `add_one&`.

You can execute the function pointed by the pointer using the [EXEC](intrinsics#EXEC) intrinsic.

```pascal
include "std"
function add_one int -> int :
    1 +
end

function increment int -> int :
    add_one&    // Push pointer to `add_one` function
    exec        // Execute the function pointer
end

function main :
    41 increment_number putu   // Prints: 42
end
```

### int - Integer

64-bit integers are defined by just using the decimal or hexadecimal value. Hexadecimal integers are prepended with '0x'.

```pascal
  420       // 64-bit decimal
  0x420     // 64-bit hexadecimal => 1056
  +         // 420 + 0x420 = 1476
```

### ptr - Pointer

Pointers point to a location in memory. [Strings](#STR---String) are also pointers to the null-terminated string buffer. Value can be stored to a pointer's location with STORE intrinsics, and the dereferenced value can be pushed to the stack with LOAD intrinsics.

Pointer can only be created by [casting](#casting). See `malloc` function in [std](../lib/std.torth) library, which allocates memory and returns a pointer to the beginning of the allocated memory chunk.

### str - String

String literals are defined with double quotes. A defined string adds a null-terminated string buffer to the `.data` section of the executable.

A string is like a [pointer](#ptr---pointer) as it points to the address of the beginning of the string data.

**Note**: Modifying the string literals stored in the `.data` section could cause undefined behavior. It is recommended to create a copy of the string with the `str.copy` function from the [std](../lib/std.torth) and modifying the copied data instead of the string literal.

#### F-strings

F-strings are strings that can contain expressions enclosed by curly brackets `{}`. Expression is piece of Torth code with some limitations:

- Expression must return value of type `str`
- Expression cannot contain double quotes or inner curly brackets

F-strings use `str.cat` function from [std](../lib/std.torth) library under the hood to concatenate literal and variable sections of the f-string. Thus, f-strings cannot be used without including the [std](../lib/std.torth) library.

Example:

```pascal
include "std"
function main :
  "frendsick" print_name
end

function print_name name:str :
  f"Hello, {name}!\n" puts
end
```

#### Escape sequence characters

Torth supports the following escape sequence characters inside strings:

- \t => Tab
- \n => New line
- \r => Carriage return
- \e => Escape
- \\\\ => Escaped backslash

## Casting

You can cast any type to another by using the [CAST](./keywords.md#cast) keyword. It enables using a value as a parameter to [function](./keywords.md#function) which has a different type than its signature expects. Casting does not generate any assembly code and thus does not affect the effectiveness of the resulting binary.

### Examples

Cast a character to an integer and print it.

```pascal
include "std"
function main :
  // Cast character 'a' to integer representation 97
  // and call print_integer function with it being its parameter.
  // Function call would not be possible without casting because it requires an integer.
  'a' cast(int) print_integer
end

function print_integer int : puti end
```

Cast a string to `Dog` and then to `Cat` and then meow. For whatever reason...

```pascal
include "std" // Imports 'puts' function
function main :
  // Cast string to Dog
  "Coco" cast(Dog)

  // Transform the Dog into Cat because Dogs cannot meow
  cast_dog_to_cat MEOW
end

function cast_dog_to_cat Dog -> Cat :
  cast(Cat)
end

function MEOW Cat :
  // Cast the Cat back to string to print it with 'puts' function from std-library
  cast(str)       puts
  " says MEOW!\n" puts
end
```
