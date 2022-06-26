# Definitions

Definitions for consepts and keywords used in the documentation.

## Integer types

- [BOOL](types.md#bool---boolean)
- [CHAR](types.md#char---character)
- [INT](types.md#int-uint8---integer)
- [UINT8](types.md#int-uint8---integer)

## Pointer types

- [PTR](types.md#ptr---pointer)
- [STR](types.md#str---string)

## Reverse Polish Notation

Torth uses Reverse Polish Notation (RPN) in which operators _follow_ their operands. Operators like [PLUS](intrinsics.md#calculations) and [MINUS](intrinsics.md#calculations) do the calculation by popping the top two elements from the stack and pushing the result back to the stack.

```pascal
20 22 +         // 2 + 2 = 42
1 3 3 7 + + *   // 1 * (3 + (3 + 7)) => 1 * (3 + 10) => 1 * 13 = 13
3 7 + 3 + 1 *   // Same as above but ordered differently
```
