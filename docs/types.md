# Types

Torth language is statically typed. Each value pushed to the stack has a type associated with it. Typing tries to ensure that the user only performs operations that are appropriate to the values of specific types.

## Built-in types

The language supports the following built-in types:

- [any](#any)
- [bool](#bool---boolean)
- [char](#char---character)
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
function print_any any :
  cast(int) print
end
```

### bool - Boolean

Boolean values are True and False. The boolean words are case insensitive.

### char - Character

Characters are defined with single quotes. They are pushed to stack as the integer representation of the character. Thus, a character can be cast to any integer type. To print the character, it should be stored in a named [memory](keywords.md#memory) location, like in the example below.

```pascal
include "std"
memory char_array str.size end
function main :
  // char char_array[] = "abc";
  'a'   char_array        char.store
  'b'   char_array 1 ptr+ char.store
  'c'   char_array 2 ptr+ char.store
  NULL  char_array 3 ptr+ int.store

  // puts(char_array);
  char_array cast(str) puts "\n" puts
end
```

### int - Integer

64-bit integers are defined by just using the decimal or hexadecimal value. Hexadecimal integers are prepended with '0x'.

```pascal
  420       // 64-bit decimal
  0x420     // 64-bit hexadecimal => 1056
  + print   // 420 + 0x420 = 1476
```

### ptr - Pointer

Pointers point to a location in memory. Memories can be defined with the [MEMORY](./keywords.md#MEMORY) keyword. [Strings](#STR---String) are also pointers to the null-terminated string buffer. Value can be stored to a pointer's location with STORE intrinsics, and the dereferenced value can be pushed to the stack with LOAD intrinsics.

### str - String

Strings are defined with double quotes. A defined string adds a null-terminated string buffer to the `.data` section of the executable. The string can be used and modified with the same techniques as [pointers](#ptr---pointer). See Examples from [MEMORY documentation](./keywords.md#MEMORY).

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

Cast a character to an integer to print it with [print](intrinsics.md#print) intrinsic.

```pascal
function main :
  // Cast character 'a' to integer representation 97
  // and call print_integer function with it being its parameter.
  // Function call would not be possible without casting because it requires an integer.
  'a' cast(int) print_integer
end

function print_integer int : print end
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
