# Triton Architecture Reference Manual v1.0

## Introduction

This document serves as the complete reference for the Triton ternary-based processor architecture.

## Table of Contents

1. [System Overview](#system-overview)
2. [Register Architecture](#register-architecture)
3. [Instruction Encoding](#instruction-encoding)
4. [Memory Model](#memory-model)
5. [Exception Handling](#exception-handling)
6. [Performance Characteristics](#performance-characteristics)

## System Overview

### Core Specifications

| Parameter | Value |
|-----------|-------|
| Native Data Width | 32 trits (~50 bits) |
| Register File Size | 32 × 32 trits |
| Clock Frequency | 1-3 GHz (target) |
| Pipeline Depth | 7 stages |
| L1 Cache | 16 KB (I) + 16 KB (D) |
| L2 Cache | 256 KB per core |
| L3 Cache | 2-16 MB (shared) |
| Memory Bus Width | 128 bits |

### Ternary Number System

**Balanced Ternary**: States are -1, 0, +1 (often represented as T, 0, 1)

**Advantages**:
- Information capacity: 1.585 bits per trit
- Symmetric representation
- Natural negation
- Better power efficiency

## Register Architecture

### General Purpose Registers

- **r0-r31**: 32 general-purpose registers, 32 trits each
- **r0**: Hardwired to zero (architectural convenience)
- Supports balanced ternary values

### Special Purpose Registers

| Register | Name | Purpose | Width |
|----------|------|---------|-------|
| r29 | sp | Stack Pointer | 32 trits |
| r30 | fp | Frame Pointer | 32 trits |
| r31 | lr | Link Register | 32 trits |
| - | pc | Program Counter | 32 trits |
| - | status | Status Register | 8 bits |

### Status Register Bits

```
Bit 7-3: Reserved
Bit 2: Sign Flag (S)
Bit 1: Zero Flag (Z)
Bit 0: Overflow Flag (V)
```

## Instruction Encoding

### Generic Format

```
┌──────────┬───────────┬───────────┬──────────┬──────────┐
│ Opcode   │ Dest Reg  │ Src1 Reg  │ Src2 Reg │ Immediate│
│ (5 trits)│ (5 trits) │ (5 trits) │ (5 trits)│ (9 trits)│
└──────────┴───────────┴───────────┴──────────┴──────────┘
```

### Instruction Classes

#### R-Type (Register)
```
ADD rd, rs1, rs2
SUB rd, rs1, rs2
MUL rd, rs1, rs2
AND rd, rs1, rs2
OR  rd, rs1, rs2
```

#### I-Type (Immediate)
```
ADDI rd, rs, imm
SLLI rd, rs, imm
BEQ  rs1, rs2, imm
BNE  rs1, rs2, imm
```

#### M-Type (Memory)
```
LW rd, offset(rs)    ; Load Word
LB rd, offset(rs)    ; Load Byte
SW rs, offset(rd)    ; Store Word
SB rs, offset(rd)    ; Store Byte
```

## Memory Model

### Address Space

```
0x00000000 - 0x7FFFFFFF   Main Memory (2 GB)
0x80000000 - 0x9FFFFFFF   I/O and Peripheral
0xA0000000 - 0xBFFFFFFF   System Memory
0xC0000000 - 0xDFFFFFFF   Cache Control
0xE0000000 - 0xFFFFFFFF   Reserved
```

### Memory Access

- **Alignment**: 4-byte boundaries for word access
- **Endianness**: Little-endian
- **Caching**: Automatic (managed by MMU)
- **Virtual Memory**: Supported with TLB

## Exception Handling

### Exception Types

| Code | Exception | Handler |
|------|-----------|----------|
| 0 | Reset | boot_vector |
| 1 | Interrupt | interrupt_handler |
| 2 | Illegal Instruction | illegal_handler |
| 3 | Memory Fault | fault_handler |
| 4 | Overflow | overflow_handler |

## Performance Characteristics

### Pipeline Stages

1. **FETCH**: Instruction fetch from cache
2. **DECODE**: Instruction decode, register access
3. **EXECUTE**: ALU operations
4. **MEMORY**: Cache/memory access
5. **WRITE-BACK**: Register file update
6. **COMMIT**: State commitment
7. **RETIRE**: Retirement

### Latencies (in cycles)

| Operation | Latency |
|-----------|----------|
| ALU (ADD/SUB/AND/OR) | 1 |
| Multiply | 3-4 |
| Divide | 10-20 |
| L1 Cache Hit | 3 |
| L2 Cache Hit | 9 |
| L3 Cache Hit | 25-40 |
| Memory Access | 100+ |

---

For more information, see the complete [Architecture Specification](../../docs/architecture.md).
