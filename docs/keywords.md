# Keywords

This is the documentation for different keywords available in the Torth language.

  * [DO](#DO)
  * [ELIF](#ELIF)
  * [ELSE](#ELSE)
  * [END](#END)
  * [ENDIF](#ENDIF)
  * [IF](#IF)
  * [INCLUDE](#INCLUDE)
  * [MACRO](#MACRO)
  * [WHILE](#WHILE)

## DO

DO is a conditional jump to the operation after next ELIF, ELSE, ENDIF or END.

The conditional jump will occur if the condition does not match because if it does the block of code should be executed.

### Examples

#### IF, ELIF, ELSE

With IF and ELIF statements, DO is a conditional jump to the operation after the next ELIF, ELSE or ENDIF keywords.

```pascal
-4                                //  int i = -4;
if 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Negative number
```

#### WHILE

In while loop, DO is a conditional jump to operation after END.

```pascal
0 while 10 > DO                   //  int i=0; while (10 > i) { 
  1 +                             //    i++;
  "This is row " print print_int  //    printf("This is row %d\n", i);
END                               //  }

// Output:
// This is row 1
// This is row 2
// ...
// This is row 10
```

## ELIF

ELIF is an unconditional jump to the operation after ENDIF. It's also a keyword for DO to coditionally jump over.

### Examples

ELIF is a unconditional jump to the operation after ENDIF because the keyword is only reached if the previous IF or ELIF block's condition was true. DO keyword is a conditional jump to the operation after ELIF if the condition is false.

```pascal
4                                 //  int i = 4;
if 0 < DO                         //  if (0 < i)
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
if 0 < DO                         //  if (0 < i)
  "Positive number" puts          //    puts("Positive number");
ELIF 0 == DO                      //  else if (0 == i)
  "Zero" puts                     //    puts("Zero");
ELSE                              //  else
  "Negative number" puts          //    puts("Negative number");
ENDIF

// Output: Zero
```

## END

END is an unconditional jump to WHILE keyword. The loop's condition is always evaluated by the DO keyword after WHILE which is also a conditional jump to the operation after the END keyword.

### Examples

```pascal
0 WHILE 10 > DO                         //  int i=0; while (10 > i) {
  1 +                                   //    i++;
  "This is row " print print_int        //    printf("This is row %d\n", i);
END                                     //  }
"Loop over after row " print print_int  //  printf("Loop over after row %d\n", i);

// Output:
// This is row 1
// This is row 2
// ...
// This is row 10
// Loop over after row 10
```

## ENDIF

TODO

## IF

TODO

## INCLUDE

TODO

## MACRO

TODO

## WHILE

TODO