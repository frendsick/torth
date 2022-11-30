# Types

Torth language is statically typed. Each value pushed to the stack has a type associated with it. Typing tries to ensure that the user only performs operations that are appropriate to the values of specific types.

## Built-in types

The language supports the following built-in types:

- [BOOL](#bool---boolean)
- [CHAR](#char---character)
- [INT](#int---integer)
- [PTR](#ptr---pointer)
- [STR](#str---string)

### BOOL - Boolean

Boolean values are True and False. The boolean words are case insensitive.

### CHAR - Character

Characters are defined with single quotes. They are pushed to stack as the integer representation of the character. Thus, character can be cast to any integer type. To print the characted it should be stored to a named [memory](keywords.md#memory) location like in the examble below.

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

### INT - Integer

64-bit integers are defined by just using the decimal or hexadecimal value. Hexadecimal integers are prepended with '0x'.

```pascal
  420       // 64-bit decimal
  0x420     // 64-bit hexadecimal => 1056
  + print   // 420 + 0x420 = 1476
```

### PTR - Pointer

Pointers are pointing to a location in the memory. Memories can be defined with the [MEMORY](./keywords.md#MEMORY)-keyword. [Strings](#STR---String) are also pointers to the null-terminated string buffer. Value can be stored to a pointer's location with STORE intrinsics and the dereferenced value can be pushed to the stack with LOAD intrinsics.

### STR - String

Strings are defined with double quotes. Defined string adds a null-terminated string buffer to .data section of the executable. The string can be used and modified with the same techniques as [pointers](#ptr---pointer). See Examples from [MEMORY documentation](./keywords.md#MEMORY).

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

Cast a character to integer to print it with [print](intrinsics.md#print) intrinsic.

```pascal
function main :
  // Cast character 'a' to integer representation 97
  // and call print_integer function with it being its parameter.
  // Function call would not be possible without casting because it requires an integer.
  'a' cast(int) print_integer
end

function print_integer int : print end
```

Cast a string to Dog and then to Cat and then meow. For whatever reason...

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
