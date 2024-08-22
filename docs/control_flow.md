# Control flow

Control flow statements alter the execution of the program.

## RETURN Keyword

With the [RETURN](keywords.md#return) keyword, you can return from a [function](keywords.md#function). The stack state should match with the [function](keywords.md#function)'s return types at the moment of usage.

See also:

- [FUNCTION](keywords.md#function)

## IF blocks

The IF block is used for conditional execution. IF block starts with the [IF](keywords.md#if) keyword and ends with the [ENDIF](keywords.md#endif) keyword. The block can also contain zero or more [ELIF](keywords.md#elif) sections and an optional [ELSE](keywords.md#else) section.

IF block runs only the first section, which matches the section's condition. If all section conditions are false, the [ELSE](keywords.md#else) section, if present, is executed. A [boolean value](types.md#bool---boolean) is required for the condition check done by [DO-keyword](keywords.md#do). [Comparison operators](intrinsics.md#comparisons) can be used to get a boolean value from the comparison between two [integer values](definitions.md#integer-types). For comparing the equality of two strings, you can use the **streq** function from [std-library](./../lib/std.torth).

### Syntax

```pascal
IF <bool> DO
  // Execute IF section
ELIF <bool> DO
  // Execute first ELIF section
ELIF <bool> DO
  // Execute second ELIF section
ELSE
  // Execute ELSE section
ENDIF
```

### Example

```pascal
42
IF dup 1337 == DO
  "Elite\n" puts
ELIF dup 69 == DO
  "Nice\n" puts
ELIF dup 42 == DO
  "Right answer!\n" puts
ELSE
  "Else\n" puts
ENDIF
// Output: Right answer!
```

## WHILE loops

The WHILE loop executes as long as a condition remains true. A [boolean value](types.md#bool---boolean) is required for the condition check done by [DO-keyword](keywords.md#do). [Comparison operators](intrinsics.md#comparisons) can be used to get a boolean value from the comparison between two [integer values](definitions.md#integer-types). For comparing the equality of two strings, you can use the **streq** function from [std-library](./../lib/std.torth).

### Syntax

```pascal
WHILE <bool> DO
  // Do something
DONE
```

### Example

```pascal
1                                   //  int i = 1;
WHILE dup 5 > DO                    //  while(5 > i) {
  "Row " puts dup putu "\n" puts    //    printf("Row %d\n", i);
  1 +                               //    i++;
DONE drop                           //  }
```

## BREAK Statement

The [BREAK](keywords.md#break) statement, like in C, breaks out of the innermost [WHILE loop](#while-loops).

```pascal
1                                   //  int i = 1;
WHILE dup 10 >= DO                  //  while(10 >= i) {
  "Row " puts dup putu "\n" puts    //    printf("Row %d\n", i);
  IF dup 4 % 0 == DO                //    if(i % 4 == 0) {
    break                           //      break;
  ENDIF                             //    }
  1 +                               //    i++;
DONE drop                           //  }
// Output:
// Row 1
// Row 2
// Row 3
// Row 4
```

## CONTINUE Statement

The [CONTINUE](keywords.md#continue) statement, like in C, continues with the next iteration of the [WHILE loop](#while-loops). Remember to update the loop's index also before using [CONTINUE](keywords.md#continue) or you could end up in an endless loop.

```pascal
1                                   //  int i = 1;
WHILE dup 10 >= DO                  //  while(10 >= i) {
  "Row " puts dup putu "\n" puts    //    printf("Row %d\n", i);
  IF dup 4 % 0 == DO                //    if(i % 4 == 0) {
    3 +                             //      i += 3;
    continue                        //      continue;
  ENDIF                             //    }
  1 +                               //    i++;
DONE drop                           //  }
// Output:
// Row 1
// Row 2
// Row 3
// Row 4
// Row 7
// Row 8
```
