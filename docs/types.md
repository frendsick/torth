# Types

Torth language is statically typed. Each value pushed to the stack has a type associated with it. Typing tries to ensure that the user only performs operations that are appropriate to the values of specific types.

## BOOL - Boolean

Boolean values are True and False. The boolean words are case insensitive.

## CHAR - Character

Characters are defined with single quotes. They are pushed to stack as the integer representation of the character. Thus, character can be cast to any integer type. To print the characted it should be stored to a named [memory](keywords.md#memory) location like in the examble below.

```pascal
include "lib/std.torth"
memory char_array str.size end
function main -> :
  // char char_array[] = "abc";
  'a'   char_array        store_char
  'b'   char_array 1 ptr+ store_char
  'c'   char_array 2 ptr+ store_char
  NULL  char_array 3 ptr+ store_int

  // puts(char_array);
  char_array puts "\n" puts
end
```

## INT, UINT8 - Integer

64-bit integers are defined by just using the decimal or hexadecimal value. Hexadecimal integers are prepended with '0x'.

8-bit unsigned integers are defined by prepending a number between 0-255 with the letter 'u'. Example: u42.

```pascal
  420       // 64-bit decimal
  0x420     // 64-bit hexadecimal
  u139      // uint8
  - + print // 420 + 0x420 - 139 = 1337
```

## PTR - Pointer

Pointers are pointing to a location in the memory. Memories can be defined with the [MEMORY](./keywords.md#MEMORY)-keyword. [Strings](#STR---String) are also pointers to the null-terminated string buffer. Value can be stored to a pointer's location with STORE intrinsics and the dereferenced value can be pushed to the stack with LOAD intrinsics.

## STR - String

Strings are defined with double quotes. Defined string adds a null-terminated string buffer to .data section of the executable. The string can be used and modified with the same techniques as [pointers](#ptr---pointer). See Examples from [MEMORY documentation](./keywords.md#MEMORY).
