#!/bin/bash
shopt -s globstar
script_dir="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"
for example_file in $script_dir/../examples/**/*.torth; do
    echo "Compiling $example_file"
    python3 $script_dir/../torth.py $example_file
    if [ $? -ne 0 ]; then
        echo "Compiling $example_file failed"
        exit 1
    fi
done