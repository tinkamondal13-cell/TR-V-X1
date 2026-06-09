; Triton Assembly Language - Basic Examples
; Balanced Ternary Architecture

.section .data
    ; Data section for constants and initialized data
    value_one:   .word 1
    value_ten:   .word 10
    msg:         .ascii "Triton"

.section .text
    .global main
    .global fibonacci
    .global factorial
    .global sum_array

; ============================================
; FIBONACCI - Calculate Fibonacci sequence
; Input: r1 = n (number of terms)
; Output: r0 = fibonacci(n)
; ============================================
fibonacci:
    ; Prologue
    ADDI    sp, sp, -4          ; Allocate stack space
    SW      fp, 0(sp)           ; Save frame pointer
    MOV     fp, sp              ; Set new frame pointer
    
    ; Check base cases
    ADDI    r2, r0, 1           ; r2 = 1
    BLE     r1, r2, fib_base    ; if n <= 1, return n
    
    ; Non-base case: fib(n) = fib(n-1) + fib(n-2)
    ADDI    r2, r1, -1          ; r2 = n - 1
    CALL    fibonacci           ; Call fib(n-1)
    SW      r0, -4(fp)          ; Save result
    
    ADDI    r1, r1, -2          ; r1 = n - 2
    CALL    fibonacci           ; Call fib(n-2)
    
    LW      r2, -4(fp)          ; Load first result
    ADD     r0, r0, r2          ; r0 = fib(n-1) + fib(n-2)
    J       fib_done
    
fib_base:
    MOV     r0, r1              ; Return n
    
fib_done:
    ; Epilogue
    MOV     sp, fp              ; Restore stack pointer
    LW      fp, 0(sp)           ; Restore frame pointer
    ADDI    sp, sp, 4           ; Deallocate stack space
    RET                         ; Return

; ============================================
; FACTORIAL - Calculate factorial
; Input: r1 = n
; Output: r0 = n!
; ============================================
factorial:
    ADDI    r0, r0, 1           ; r0 = 1 (accumulator)
    
fact_loop:
    ADDI    r2, r1, 0           ; r2 = n (copy)
    BLE     r1, r0, fact_done   ; if n <= 1, done
    
    MUL     r0, r0, r1          ; r0 = r0 * n
    ADDI    r1, r1, -1          ; n = n - 1
    J       fact_loop           ; Continue
    
fact_done:
    RET                         ; Return

; ============================================
; SUM_ARRAY - Sum array elements
; Input: r1 = array address, r2 = array length
; Output: r0 = sum
; ============================================
sum_array:
    ADDI    r0, r0, 0           ; r0 = 0 (sum accumulator)
    ADDI    r3, r0, 0           ; r3 = 0 (index)
    
sum_loop:
    BGE     r3, r2, sum_done    ; if index >= length, done
    
    ; Calculate address: r4 = r1 + (r3 * 4)
    MUL     r4, r3, 4           ; r4 = index * 4
    ADD     r4, r4, r1          ; r4 = array_addr + offset
    
    LW      r5, 0(r4)           ; r5 = array[index]
    ADD     r0, r0, r5          ; sum += array[index]
    
    ADDI    r3, r3, 1           ; index++
    J       sum_loop            ; Continue loop
    
sum_done:
    RET                         ; Return

; ============================================
; MAIN - Entry point
; ============================================
main:
    ; Test Fibonacci
    ADDI    r1, r0, 10          ; Calculate fib(10)
    JAL     lr, fibonacci       ; Call fibonacci
    SW      r0, result_fib      ; Store result
    
    ; Test Factorial
    ADDI    r1, r0, 5           ; Calculate 5!
    JAL     lr, factorial       ; Call factorial
    SW      r0, result_fact     ; Store result
    
    ; Test Array Sum
    LA      r1, test_array      ; Load array address
    ADDI    r2, r0, 5           ; Array length = 5
    JAL     lr, sum_array       ; Call sum_array
    SW      r0, result_sum      ; Store result
    
    ; Exit
    HALT                        ; Halt processor

.section .data
    test_array:     .word 1, 2, 3, 4, 5
    result_fib:     .word 0
    result_fact:    .word 0
    result_sum:     .word 0
