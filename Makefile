all: bootstrap/torth.asm
	nasm -f elf64 -o torth.o bootstrap/torth.asm
	ld -m elf_x86_64 -s -o torth torth.o

clean:
	rm -f *.asm
	rm -f *.o
