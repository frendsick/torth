# Definitions

Definitions for consepts and keywords used in the documentation.

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
- [INT](types.md#int-uint8---integer)
- [UINT8](types.md#int-uint8---integer)

**Note**: Function parameter and return values MUST be exactly the types that the function signature implies. You can always explicitely cast another type to integer-like type by using the type as token. For example, if you want to cast a value to [INT](types.md#int-uint8---integer), use `int` keyword.

See also: [Casting](keywords.md#casting)

## Pointer types

The following types count as pointer-like types whenever an intrinsic requires them in the stack:

- [PTR](types.md#ptr---pointer)
- [STR](types.md#str---string)

Note: Function parameter and return values MUST be exactly the types that the function signature implies. You can always explicitely cast an pointer-like type to another pointer-like type by using the type as token. Also, you can cast some integer-like types to [PTR](types.md#ptr---pointer). For example, if you want to cast a value to PTR, use `ptr` keyword.

See also: [Casting](keywords.md#casting)

## PATH

PATH defines relative directories compared to the compiler file [torth.py](../torth.py) from which additional files can be included to the code with [INCLUDE](keywords.md#include) keyword. The files at the same directory as the compiler will always take precedence over any files from PATH.

Default directories in PATH:

```python
PATH = [
  'lib'
]
```

When including a file, the first matching file in PATH will be included. Additional directories can added to PATH with the `--path` command line argument to [torth.py](../torth.py). It is a comma separated list of directories that are added to PATH. Directories defined in the command line argument take precedence over the default PATH directories.
