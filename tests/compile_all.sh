#!/bin/bash
shopt -s globstar
script_dir="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"
for example_file in $script_dir/../examples/**/*.torth; do
    echo "[INFO] Compiling $example_file"
    python3 $script_dir/../torth.py $example_file
    if [ $? -ne 0 ]; then
        echo "[ERROR] Compiling $example_file failed"
    fi
done