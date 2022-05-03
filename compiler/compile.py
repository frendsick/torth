import subprocess

def compile_asm(asm_file: str) -> None:
    subprocess.run(['nasm', '-felf64', f'-o{asm_file.replace(".asm", ".o")}', asm_file])

def link_object_file(obj_file: str, output_file: str) -> None:
    subprocess.run(['gcc', '-no-pie', f'-o{output_file}', obj_file])
