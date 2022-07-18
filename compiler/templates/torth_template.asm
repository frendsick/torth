default rel

;; DEFINES
%define sys_exit 60
section .data

section .bss
  args_ptr: resq 1
  return_stack: resb 1337*64
  return_stack_index: resq 1

section .text

;; Joinked from Porth's print function, thank you Tsoding!
print:
  mov     r9, -3689348814741910323
  sub     rsp, 40
  lea     rcx, [rsp+30]
.L2:
  mov     rax, rdi
  lea     r8, [rsp+32]
  mul     r9
  mov     rax, rdi
  sub     r8, rcx
  shr     rdx, 3
  lea     rsi, [rdx+rdx*4]
  add     rsi, rsi
  sub     rax, rsi
  add     eax, 48
  mov     BYTE [rcx], al
  mov     rax, rdi
  mov     rdi, rdx
  mov     rdx, rcx
  sub     rcx, 1
  cmp     rax, 9
  ja      .L2
  lea     rax, [rsp+32]
  mov     edi, 1
  sub     rdx, rax
  xor     eax, eax
  lea     rsi, [rsp+32+rdx]
  dec     r8
  mov     rdx, r8
  mov     rax, 1
  syscall
  add     rsp, 40
  ret

global _start
_start:
  mov [args_ptr], rsp   ; Pointer to argc
