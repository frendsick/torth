# Definitions

Definitions for consepts and keywords used in the documentation.

## Reverse Polish Notation

Torth uses Reverse Polish Notation (RPN) in which operators _follow_ their operands. Operators like [PLUS](intrinsics.md#calculations) and [MINUS](intrinsics.md#calculations) do the calculation by popping the top two elements from the stack and pushing the result back to the stack.

```pascal
20 22 +         // 2 + 2 = 42
1 3 3 7 + + *   // 1 * (3 + (3 + 7)) => 1 * (3 + 10) => 1 * 13 = 13
3 7 + 3 + 1 *   // Same as above but ordered differently
```

## Integer types

The following types count as integer-like types whenever an intrinsic requires them in the stack:

- [BOOL](types.md#bool---boolean)
- [CHAR](types.md#char---character)
- [INT](types.md#int-uint8---integer)
- [UINT8](types.md#int-uint8---integer)

Note: Function parameter and return values MUST be exactly the types that the function signature implies. You can always explicitely cast an integer-like type to another integer-like type by using the type as token. For example, if you want to cast any integer-like type to CHAR, use `char` keyword.

## Pointer types

The following types count as pointer-like types whenever an intrinsic requires them in the stack:

- [PTR](types.md#ptr---pointer)
- [STR](types.md#str---string)

Note: Function parameter and return values MUST be exactly the types that the function signature implies. You can always explicitely cast an pointer-like type to another pointer-like type by using the type as token. For example, if you want to cast any pointer-like type to STR, use `str` keyword.
