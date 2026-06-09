; Triton Matrix Multiplication Kernel
; Multiply two 4x4 matrices

.section .data
    ; Input matrices (in memory)
    matrix_a:       .word 1, 2, 3, 4
                    .word 5, 6, 7, 8
                    .word 9, 10, 11, 12
                    .word 13, 14, 15, 16
    
    matrix_b:       .word 1, 0, 0, 0
                    .word 0, 1, 0, 0
                    .word 0, 0, 1, 0
                    .word 0, 0, 0, 1
    
    result:         .word 0, 0, 0, 0
                    .word 0, 0, 0, 0
                    .word 0, 0, 0, 0
                    .word 0, 0, 0, 0

.section .text
    .global matrix_mul_4x4
    
; Matrix multiplication 4x4
; r1 = address of matrix A
; r2 = address of matrix B
; r3 = address of result matrix
matrix_mul_4x4:
    ADDI    r4, r0, 0           ; i = 0 (row counter)
    
outer_loop:
    BGE     r4, 4, mul_done
    
    ADDI    r5, r0, 0           ; j = 0 (column counter)
    
inner_loop:
    BGE     r5, 4, next_row
    
    ; Calculate element [i,j]
    ADDI    r6, r0, 0           ; sum = 0
    ADDI    r7, r0, 0           ; k = 0 (dot product counter)
    
dot_product:
    BGE     r7, 4, store_element
    
    ; Load A[i][k]
    MUL     r8, r4, 16          ; offset = i * 4 * 4
    MUL     r9, r7, 4           ; offset += k * 4
    ADD     r8, r8, r9
    ADD     r8, r8, r1          ; address = A + offset
    LW      r10, 0(r8)          ; load A[i][k]
    
    ; Load B[k][j]
    MUL     r8, r7, 16          ; offset = k * 4 * 4
    MUL     r9, r5, 4           ; offset += j * 4
    ADD     r8, r8, r9
    ADD     r8, r8, r2          ; address = B + offset
    LW      r11, 0(r8)          ; load B[k][j]
    
    ; Multiply and accumulate
    MUL     r12, r10, r11       ; temp = A[i][k] * B[k][j]
    ADD     r6, r6, r12         ; sum += temp
    
    ADDI    r7, r7, 1           ; k++
    J       dot_product
    
store_element:
    ; Store result[i][j]
    MUL     r8, r4, 16          ; offset = i * 4 * 4
    MUL     r9, r5, 4           ; offset += j * 4
    ADD     r8, r8, r9
    ADD     r8, r8, r3          ; address = result + offset
    SW      r6, 0(r8)           ; store sum
    
    ADDI    r5, r5, 1           ; j++
    J       inner_loop
    
next_row:
    ADDI    r4, r4, 1           ; i++
    J       outer_loop
    
mul_done:
    RET
