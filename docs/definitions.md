# Definitions

Definitions for concepts and keywords used in the documentation.

## Reverse Polish Notation

Torth uses Reverse Polish Notation (RPN) in which operators _follow_ their operands. Operators like [PLUS](intrinsics.md#calculations) and [MINUS](intrinsics.md#calculations) do the calculation by popping the top two elements from the stack and pushing the result back to the stack.

```pascal
20 22 +         // 22 + 20 = 42
1 3 3 7 + + *   // 1 * (3 + (3 + 7)) => 1 * (3 + 10) => 1 * 13 = 13
3 7 + 3 + 1 *   // Same as above but ordered differently
```

## Integer types

The following types count as integer-like types whenever an intrinsic requires them in the stack:

- [BOOL](types.md#bool---boolean)
- [CHAR](types.md#char---character)
- [INT](types.md#int---integer)

**Note**: Function parameter and return values must be exactly the types that the function signature implies. You can use [casting](types.md#casting) to change the type of a value.

## Pointer types

The following types count as pointer-like types whenever an intrinsic requires them in the stack:

- [PTR](types.md#ptr---pointer)
- [STR](types.md#str---string)

Note: Function parameter and return values must be exactly the types that the function signature implies. You can use [casting](types.md#casting) to change the type of a value.

## PATH

PATH defines relative directories compared to the compiler file [torth.torth](../torth.torth), from which additional files can be included in the code with the [INCLUDE](keywords.md#include) keyword. The files in the same directory as the compiler will always take precedence over any files from PATH.

Default directories in PATH:

```python
PATH = [
  'lib'
]
```

It is not yet possible to add folders to PATH with command line arguments.
