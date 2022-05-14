# Keywords

This is the documentation for different keywords available in the Torth language.

- [BREAK](#BREAK)
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

### Examples

```pascal
0 WHILE dup 10 > DO
  1 + print_int
  IF 3 == DO
    "Breaking from loop..." puts
    BREAK
  ENDIF
DONE
// Output:
1
2
3
Breaking from loop...
```

## DO

DO is a conditional jump to the operation after next ELIF, ELSE, ENDIF or DONE.

The conditional jump will occur if the condition does not match because if it does the block of code should be executed.

### Examples

#### IF, ELIF, ELSE

With IF and ELIF statements, DO is a conditional jump to the operation after the next ELIF, ELSE or ENDIF keywords.

```pascal
-4                                //  int i = -4;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Negative number
```

#### WHILE

In while loop, DO is a conditional jump to operation after DONE.

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

### Examples

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

### Examples

ELIF is a unconditional jump to the operation after ENDIF because the keyword is only reached if the previous IF or ELIF block's condition was true. DO keyword is a conditional jump to the operation after ELIF if the condition is false.

```pascal
4                                 //  int i = 4;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Positive number
```

## ELSE

ELSE is an unconditional jump to the operation after ENDIF. It's also a keyword for DO to coditionally jump over.

### Examples

ELSE is a unconditional jump to the operation after ENDIF because the keyword is only reached if the previous IF or ELIF block's condition was true. DO keyword is a conditional jump to the operation after ELSE if the condition is false.

```pascal
0                                 //  int i = 0;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
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
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ENDIF
"This is after ENDIF" puts        //  puts("This is after ENDIF");

// Output:
// Positive number
// This is after ENDIF
```

```pascal
0                                 //  int i = 0;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
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
  if 18 > do
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

IF keyword is like DUP intrinsic, it duplicates the first element in the stack so that there is no need to manually duplicate the topmost element in the stack for the purpose of IF statement comparisation.

### Examples

```pascal
4                                 //  int i = 4;
IF 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ENDIF

// Output:
// Positive number
```

## WHILE

WHILE is a keyword for DONE to jump to.

### Examples

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
