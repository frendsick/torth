# Keywords

This is the documentation for different keywords available in the Torth language.

- [BREAK](#BREAK)
- [CONST](#CONST)
- [DO](#DO)
- [DONE](#DONE)
- [ELIF](#ELIF)
- [ELSE](#ELSE)
- [ENDIF](#ENDIF)
- [FUNCTION](#FUNCTION)
- [IF](#IF)
- [WHILE](#WHILE)

## BREAK

BREAK is unconditional jump to the operation after DONE of the current loop.

```pascal
0 WHILE dup 10 > DO
  1 + print_int
  IF dup 3 == DO
    "Breaking from the loop...\n" puts
    BREAK
  ENDIF
DONE
// Output:
1
2
3
Breaking from the loop...
```

## CONST

Constants are named integer values that cannot be modified. The constant name can be used in code to push the constant's integer value to the stack. Constants can also be used in [MEMORY](#MEMORY) declarations when defining the size of the memory. However, constants cannot be used in defining other constants at least for now.

### Syntax

```pascal
CONST <name> <integer> END
```

### Examples

```pascal
include "lib/std.torth"
const ptr.size 8 end
memory dst ptr.size end
memory src ptr.size end

function main -> :
  1337 src int.store          // Store 1337 to src
  9001 dst int.store          // Store 9001 to dst
  src int.load dst int.store  // Copy the value from src to dst
  src int.load print          // Print the value 1337 from src
  dst int.load print          // Print the value 1337 from dst
end  // Expected output: 13371337
```

## DO

DO is a conditional jump to the operation after next ELIF, ELSE, ENDIF or DONE.

The conditional jump will occur if the condition does not match because if it does the block of code should be executed.

With IF and ELIF statements, DO is a conditional jump to the operation after the next ELIF, ELSE or ENDIF keywords.

In while loop, DO is a conditional jump to operation after DONE.

### Examples

```pascal
-4                                //  int i = -4;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF dup 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Negative number
```

```pascal
0 WHILE dup 10 > DO                   //  int i=0; while (10 > i) {
  1 +                             //    i++;
  "This is row " print print_int  //    printf("This is row %d\n", i);
DONE                               //  }

// Output:
// This is row 1
// This is row 2
// ...
// This is row 10
```

## DONE

DONE is an unconditional jump to WHILE keyword. The loop's condition is always evaluated by the DO keyword after WHILE which is also a conditional jump to the operation after the DONE keyword.

```pascal
0 WHILE dup 10 > DO                         //  int i=0; while (10 > i) {
  1 +                                   //    i++;
  "This is row " print print_int        //    printf("This is row %d\n", i);
DONE                                     //  }
"Loop over after row " print print_int  //  printf("Loop over after row %d\n", i);

// Output:
// This is row 1
// This is row 2
// ...
// This is row 10
// Loop over after row 10
```

## ELIF

ELIF is an unconditional jump to the operation after ENDIF. It's also a keyword for DO to coditionally jump over.

ELIF is a unconditional jump to the operation after ENDIF because the keyword is only reached if the previous IF or ELIF block's condition was true. DO keyword is a conditional jump to the operation after ELIF if the condition is false.

```pascal
4                                 //  int i = 4;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF dup 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Positive number
```

## ELSE

ELSE is an unconditional jump to the operation after ENDIF. It's also a keyword for DO to coditionally jump over.

ELSE is a unconditional jump to the operation after ENDIF because the keyword is only reached if the previous IF or ELIF block's condition was true. DO keyword is a conditional jump to the operation after ELSE if the condition is false.

```pascal
0                                 //  int i = 0;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF dup 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Zero
```

## ENDIF

ENDIF is a keyword for DO, ELIF, or ELSE keywords to jump over.

### Examples

```pascal
0                                 //  int i = 0;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ENDIF
"This is after ENDIF" puts        //  puts("This is after ENDIF");

// Output: This is after ENDIF
```

```pascal
4                                 //  int i = 0;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF dup 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ENDIF
"This is after ENDIF" puts        //  puts("This is after ENDIF");

// Output:
// Positive number
// This is after ENDIF
```

```pascal
0                                 //  int i = 0;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF dup 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF
"This is after ENDIF" puts        //  puts("This is after ENDIF");

// Output:
// Zero
// This is after ENDIF
```

## FUNCTION

Functions are defined using FUNCTION keyword. Functions are pieces of code that can be called from wherever inside the program by using its name as token. When called, the function's name is replaced with the contents of the function during compilation. Functions should be defined before calling. Defined functions are case sensitive tokens unlike most other keywords in Torth.

Functions do not take parameters but instead use the current stack. Function syntax encourages the programmer to document the params used in the function and how it alters stack's state during it's execution.

### Syntax

```pascal
// Different tokens or words can be on different lines
FUNCION <name> <args> -> <return_values> END
```

### Examples

```pascal
// Example with name and age as parameters, name is on top of the stack
// Note: Strings pushes two items to the stack, it's length and pointer to the string buffer
function is_adult str_buf* int int -> bool :
  print // Prints name
  if dup 18 > do
    False " you are not an adult"
  else
    True  " you are an adult"
  endif puts // Prints
end

function main -> :
  42 "Teemu" is_adult
  "Return value: " print print_int // Output: 40
end
```

```pascal
FUNCTION multiply_by_two int -> int : 2 * END

// Functions can be called from within another function
function MultiplyByFour
  int
  ->
  int :
    multiply_by_two
    multiply_by_two
end

function main -> :
  5 multiply_by_two MultiplyByFour print_int  // Output: 40
end
```

## IF

IF is just a keyword which starts an IF-block. IF-block ends to (ENDIF)[#ENDIF].

```pascal
4                                 //  int i = 4;
IF dup 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ENDIF

// Output:
// Positive number
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
include "lib/std.torth"
memory leet int.size end  // int.size = 8
memory feet ptr.size end  // ptr.size = 8
function main -> :
  1337 leet store_INT
  leet load_INT print "\n" puts // Output: 1337

  "pinky\n" feet store_STR
  'k' feet load_PTR store_CHAR
  feet load_STR puts            // Output: kinky
end
```

## WHILE

WHILE is a keyword for DONE to jump to.

```pascal
0 WHILE dup 10 > DO                         //  int i=0; while (10 > i) {
  1 +                                   //    i++;
  "This is row " print print_int        //    printf("This is row %d\n", i);
DONE                                     //  }
"Loop over after row " print print_int  //  printf("Loop over after row %d\n", i);

// Output:
// This is row 1
// This is row 2
// ...
// This is row 10
// Loop over after row 10
```
