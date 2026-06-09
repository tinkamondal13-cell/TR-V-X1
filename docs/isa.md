# Triton Instruction Set Architecture (ISA)

## Overview

The Triton ISA defines the interface between hardware and software. It is optimized for ternary computation while maintaining elegant orthogonality.

## Instruction Format

### General Format

```
┌─────────────┬──────────┬──────────┬──────────┬──────────┐
│ Opcode      │ Register │ Register │ Operand  │ Operand  │
│ (5 trits)   │ Dest (5) │ Src1 (5) │ Src2 (5) │ Field (9)│
└─────────────┴──────────┴──────────┴──────────┴──────────┘
         Total: 29 trits per instruction
```

### Instruction Classes

1. **Arithmetic Instructions** - Ternary arithmetic operations
2. **Logic Instructions** - Ternary bitwise operations
3. **Memory Instructions** - Load/Store operations
4. **Control Instructions** - Branches and jumps
5. **Special Instructions** - System and privileged operations

## Register File

### General Purpose Registers

- **Count**: 32 registers (r0-r31)
- **Width**: 32 trits each (~50 bits effective)
- **r0**: Hardwired zero (architectural convenience)

### Special Purpose Registers

| Register | Name | Purpose |
|----------|------|----------|
| sp | Stack Pointer | Stack management |
| fp | Frame Pointer | Function frames |
| lr | Link Register | Return addresses |
| pc | Program Counter | Instruction pointer |
| status | Status Register | Flags and control |

## Instruction Categories

### Arithmetic Instructions

```
ADD Rd, Rs1, Rs2    - Ternary addition
SUB Rd, Rs1, Rs2    - Ternary subtraction
MUL Rd, Rs1, Rs2    - Ternary multiplication
DIV Rd, Rs1, Rs2    - Ternary division
MOD Rd, Rs1, Rs2    - Ternary modulo
ADDI Rd, Rs, imm    - Add immediate
```

### Logic Instructions

```
AND Rd, Rs1, Rs2    - Ternary AND
OR Rd, Rs1, Rs2     - Ternary OR
XOR Rd, Rs1, Rs2    - Ternary XOR
NOT Rd, Rs          - Ternary NOT
SHL Rd, Rs, shift   - Shift left
SHR Rd, Rs, shift   - Shift right
```

### Memory Instructions

```
LW Rd, offset(Rs)   - Load word (32 trits)
LB Rd, offset(Rs)   - Load byte (8 trits)
SW Rs, offset(Rd)   - Store word
SB Rs, offset(Rd)   - Store byte
LLW Rd, offset(Rs)  - Load linked word (for atomic ops)
SCW Rs, offset(Rd)  - Store conditional word
```

### Control Instructions

```
BEQ Rs1, Rs2, label - Branch if equal
BNE Rs1, Rs2, label - Branch if not equal
BLT Rs1, Rs2, label - Branch if less than
BGE Rs1, Rs2, label - Branch if greater/equal
J label             - Unconditional jump
JAL Rd, label       - Jump and link (call)
RET                 - Return from function
CALL offset         - Call subroutine
```

### Special Instructions

```
NOP                 - No operation
HALT                - Halt processor
SYSCALL             - System call
BREAK               - Breakpoint
FENCE               - Memory fence
```

## Ternary Operations Reference

### Basic Ternary Logic

**AND Operation**
```
A | B | A AND B
--|---|--------
-1|-1 |  -1
-1| 0 |  -1
-1|+1 |  -1
 0|-1 |  -1
 0| 0 |   0
 0|+1 |   0
+1|-1 |  -1
+1| 0 |   0
+1|+1 |  +1
```

**OR Operation**
```
A | B | A OR B
--|---|-------
-1|-1 |  -1
-1| 0 |  -1
-1|+1 |  +1
 0|-1 |  -1
 0| 0 |   0
 0|+1 |  +1
+1|-1 |  +1
+1| 0 |  +1
+1|+1 |  +1
```

## Assembly Syntax

### Basic Format

```assembly
label:  instruction operand1, operand2, operand3  # comment
```

### Example Program

```assembly
; Ternary Fibonacci
.section .text
.global main

main:
    ADDI    r1, r0, 1      ; r1 = 1 (first Fibonacci number)
    ADDI    r2, r0, 1      ; r2 = 1 (second Fibonacci number)
    ADDI    r3, r0, 10     ; r3 = 10 (loop counter)
    
fib_loop:
    ADD     r4, r1, r2     ; r4 = r1 + r2
    MOV     r1, r2         ; r1 = r2
    MOV     r2, r4         ; r2 = r4
    SUBI    r3, r3, 1      ; r3 = r3 - 1
    BNE     r3, r0, fib_loop ; if r3 != 0, continue
    
    MOV     r0, r2         ; return value in r0
    RET                     ; return
```

## Calling Convention

### Parameter Passing

- Arguments 1-4: r1-r4
- Additional args: Stack (right-to-left)
- Return value: r0

### Register Preservation

- Caller-saved: r1-r11
- Callee-saved: r12-r31, sp, fp

## Addressing Modes

1. **Register**: `ADD r1, r2, r3`
2. **Immediate**: `ADDI r1, r2, 100`
3. **Indirect**: `LW r1, (r2)`
4. **Indexed**: `LW r1, 100(r2)`
5. **PC-Relative**: `J offset` (automatic)

## Exception Handling

### Exception Types

| Code | Exception | Handler |
|------|-----------|----------|
| 0 | Reset | boot_vector |
| 1 | Interrupt | interrupt_handler |
| 2 | Illegal Instruction | illegal_handler |
| 3 | Memory Fault | fault_handler |
| 4 | Overflow | overflow_handler |

---

For implementation details and microcode, see the hardware documentation.
