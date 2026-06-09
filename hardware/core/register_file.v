// Triton Register File
// 32 registers × 32 trits each

module triton_register_file #(
    parameter NUM_REGS = 32,
    parameter REG_WIDTH = 32
) (
    input                          clk,
    input                          reset_n,
    input  [4:0]                   rd_addr1,    // Read port 1 address
    input  [4:0]                   rd_addr2,    // Read port 2 address
    input  [4:0]                   wr_addr,     // Write port address
    input  [REG_WIDTH*2-1:0]       wr_data,     // Write data (balanced ternary)
    input                          wr_enable,   // Write enable
    output reg [REG_WIDTH*2-1:0]   rd_data1,    // Read data port 1
    output reg [REG_WIDTH*2-1:0]   rd_data2     // Read data port 2
);

    // Register file storage (balanced ternary: each trit is 2 bits)
    reg [REG_WIDTH*2-1:0] registers [0:NUM_REGS-1];

    // Special register indices
    localparam REG_ZERO = 5'd0;      // r0 - Always zero
    localparam REG_SP   = 5'd29;     // r29 - Stack pointer
    localparam REG_FP   = 5'd30;     // r30 - Frame pointer  
    localparam REG_LR   = 5'd31;     // r31 - Link register

    // Initialize registers
    initial begin
        integer i;
        for (i = 0; i < NUM_REGS; i = i + 1) begin
            registers[i] = 64'h0;
        end
        // Initialize stack pointer to high memory
        registers[REG_SP] = 64'hFFFFFFFFFFFFFFFF;
    end

    // Asynchronous read - Read port 1
    always @(*) begin
        if (rd_addr1 == REG_ZERO) begin
            rd_data1 = 64'h0;  // r0 is always zero
        end else begin
            rd_data1 = registers[rd_addr1];
        end
    end

    // Asynchronous read - Read port 2
    always @(*) begin
        if (rd_addr2 == REG_ZERO) begin
            rd_data2 = 64'h0;  // r0 is always zero
        end else begin
            rd_data2 = registers[rd_addr2];
        end
    end

    // Synchronous write
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            integer i;
            for (i = 0; i < NUM_REGS; i = i + 1) begin
                registers[i] <= 64'h0;
            end
            registers[REG_SP] <= 64'hFFFFFFFFFFFFFFFF;
        end else if (wr_enable && wr_addr != REG_ZERO) begin
            // r0 is read-only (always zero)
            registers[wr_addr] <= wr_data;
        end
    end

endmodule
