default rel

;; DEFINES
%define sys_exit 60
section .data

section .bss
  args_ptr: resq 1
  return_stack: resb 1337*64
  return_stack_index: resq 1
