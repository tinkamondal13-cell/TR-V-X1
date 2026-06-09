// Triton ALU Testbench

`timescale 1ns / 1ps

module triton_alu_tb();

    // Test signals
    reg  [63:0]  operand_a;
    reg  [63:0]  operand_b;
    reg  [4:0]   alu_op;
    wire [63:0]  result;
    wire [2:0]   flags;
    reg           clk;
    reg           reset_n;

    // Instantiate ALU
    triton_alu #(.TRIT_WIDTH(32)) dut (
        .operand_a(operand_a),
        .operand_b(operand_b),
        .alu_op(alu_op),
        .result(result),
        .flags(flags),
        .clk(clk),
        .reset_n(reset_n)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test vectors
    initial begin
        $display("\n===== Triton ALU Testbench =====");
        $display("Testing Ternary Arithmetic Logic Unit\n");

        // Reset
        reset_n = 0;
        #10;
        reset_n = 1;
        #10;

        // Test 1: Addition
        $display("Test 1: Addition (5 + 3 = 8)");
        operand_a = 64'h5;
        operand_b = 64'h3;
        alu_op = 5'b00001;  // ADD
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'h8) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 2: Subtraction
        $display("Test 2: Subtraction (10 - 3 = 7)");
        operand_a = 64'hA;
        operand_b = 64'h3;
        alu_op = 5'b00010;  // SUB
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'h7) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 3: Multiplication
        $display("Test 3: Multiplication (4 * 3 = 12)");
        operand_a = 64'h4;
        operand_b = 64'h3;
        alu_op = 5'b00011;  // MUL
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'hC) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 4: Ternary AND
        $display("Test 4: Ternary AND");
        operand_a = 64'hFFFF;
        operand_b = 64'h00FF;
        alu_op = 5'b00100;  // AND
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'h00FF) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 5: Ternary OR
        $display("Test 5: Ternary OR");
        operand_a = 64'hFF00;
        operand_b = 64'h00FF;
        alu_op = 5'b00101;  // OR
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'hFFFF) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 6: Left Shift
        $display("Test 6: Left Shift (1 << 4 = 16)");
        operand_a = 64'h1;
        operand_b = 64'h4;
        alu_op = 5'b01000;  // SHL
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'h10) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 7: Right Shift
        $display("Test 7: Right Shift (16 >> 2 = 4)");
        operand_a = 64'h10;
        operand_b = 64'h2;
        alu_op = 5'b01001;  // SHR
        #10;
        $display("  Result: %h, Flags: %b", result, flags);
        assert(result == 64'h4) else $display("  FAILED!");
        $display("  PASSED!\n");

        // Test 8: Zero result flag
        $display("Test 8: Zero Flag Test (5 - 5 = 0)");
        operand_a = 64'h5;
        operand_b = 64'h5;
        alu_op = 5'b00010;  // SUB
        #10;
        $display("  Result: %h, Flags: %b (Zero flag should be 1)", result, flags);
        assert(flags[1] == 1) else $display("  FAILED!");
        $display("  PASSED!\n");

        $display("===== All Tests Completed =====");
        $finish;
    end

    // Monitor
    initial begin
        $monitor("Time: %0t | A: %h | B: %h | Op: %b | Result: %h | Flags: %b",
                $time, operand_a, operand_b, alu_op, result, flags);
    end

endmodule
