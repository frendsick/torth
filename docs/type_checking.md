# Type checking

Torth language is statically typed. Each value pushed to the stack has a type associated with it. Typing tries to ensure that the user only performs operations that are appropriate to the values of specific types.

## Types

- BOOL
- CHAR
- INT
- PTR
- STR
- UINT8

### BOOL - Boolean

Boolean values are True and False. The boolean words are case insensitive.

### CHAR - Character

Characters are defined with single quotes. They are pushed to stack as the integer representation of the character. Thus, character can be cast to any integer type. To print the characted it should be stored to a named memory location like in the examble below.

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
