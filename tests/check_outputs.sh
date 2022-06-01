#!/bin/bash
shopt -s globstar
script_dir="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"
output_errors=0

# Compile all examples
$script_dir/compile_all.sh

for executable in $script_dir/../*.bin; do
  exe_basename=$(basename -s .bin "$executable")
  echo "[INFO] Running $executable"
  diff -u $script_dir/outputs/$exe_basename.txt <($executable)

  if [ $? -ne 0 ]; then
    echo "[ERROR] $exe_basename.bin output differs from outputs/$exe_basename.txt"
    ((output_errors+=1))
  fi
done

if [ $output_errors -ne 0 ]; then
  echo "[ERROR] Example outputs differed from the prerecorded tests for $output_errors example(s)"
  exit 1
fi