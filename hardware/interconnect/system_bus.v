// Triton System Bus (Interconnect)
// Hierarchical crossbar with ternary arbitration

module triton_system_bus #(
    parameter NUM_MASTERS = 4,
    parameter NUM_SLAVES = 4,
    parameter ADDR_WIDTH = 32,
    parameter DATA_WIDTH = 64
) (
    input                               clk,
    input                               reset_n,
    
    // Master ports (from cores/DMA)
    input  [NUM_MASTERS-1:0][ADDR_WIDTH-1:0]     m_addr,
    input  [NUM_MASTERS-1:0][DATA_WIDTH-1:0]     m_write_data,
    output [NUM_MASTERS-1:0][DATA_WIDTH-1:0]     m_read_data,
    input  [NUM_MASTERS-1:0]                     m_valid,
    input  [NUM_MASTERS-1:0]                     m_write,
    output [NUM_MASTERS-1:0]                     m_ready,
    
    // Slave ports (to memories/peripherals)
    output reg [NUM_SLAVES-1:0][ADDR_WIDTH-1:0]  s_addr,
    output reg [NUM_SLAVES-1:0][DATA_WIDTH-1:0]  s_write_data,
    input  [NUM_SLAVES-1:0][DATA_WIDTH-1:0]      s_read_data,
    output reg [NUM_SLAVES-1:0]                  s_valid,
    output reg [NUM_SLAVES-1:0]                  s_write,
    input  [NUM_SLAVES-1:0]                      s_ready
);

    // Arbitration signals
    reg [$clog2(NUM_MASTERS)-1:0] grant [0:NUM_SLAVES-1];
    wire [NUM_MASTERS-1:0] request [0:NUM_SLAVES-1];
    
    // Slave address decoder
    function [NUM_SLAVES-1:0] decode_slave;
        input [ADDR_WIDTH-1:0] addr;
        begin
            // Simple address decoding
            // Slaves mapped to address ranges
            if (addr < 32'h80000000)
                decode_slave = 4'b0001;  // Slave 0: Main Memory
            else if (addr < 32'hA0000000)
                decode_slave = 4'b0010;  // Slave 1: I/O
            else if (addr < 32'hC0000000)
                decode_slave = 4'b0100;  // Slave 2: Peripheral
            else
                decode_slave = 4'b1000;  // Slave 3: System
        end
    endfunction

    // Ternary Arbitration Logic
    // Priority: Master 0 > Master 1 > Master 2 > Master 3
    always @(*) begin
        integer i, j;
        
        // Generate request signals for each slave
        for (i = 0; i < NUM_SLAVES; i = i + 1) begin
            for (j = 0; j < NUM_MASTERS; j = j + 1) begin
                request[i][j] = m_valid[j] && (decode_slave(m_addr[j]) == (1 << i));
            end
        end
        
        // Arbitration for each slave
        for (i = 0; i < NUM_SLAVES; i = i + 1) begin
            grant[i] = 0;
            for (j = 0; j < NUM_MASTERS; j = j + 1) begin
                if (request[i][j]) begin
                    grant[i] = j;
                    break;
                end
            end
        end
    end

    // Master side - ready signals
    always @(*) begin
        integer i;
        for (i = 0; i < NUM_MASTERS; i = i + 1) begin
            m_ready[i] = 1'b0;
        end
        
        for (i = 0; i < NUM_SLAVES; i = i + 1) begin
            m_ready[grant[i]] = s_ready[i];
        end
    end

    // Slave side - address, data, and control signals
    always @(*) begin
        integer i, j;
        for (i = 0; i < NUM_SLAVES; i = i + 1) begin
            s_addr[i] = 32'h0;
            s_write_data[i] = 64'h0;
            s_valid[i] = 1'b0;
            s_write[i] = 1'b0;
            
            for (j = 0; j < NUM_MASTERS; j = j + 1) begin
                if (grant[i] == j && m_valid[j]) begin
                    s_addr[i] = m_addr[j];
                    s_write_data[i] = m_write_data[j];
                    s_valid[i] = 1'b1;
                    s_write[i] = m_write[j];
                end
            end
        end
    end

    // Read data multiplexing
    genvar k;
    generate
        for (k = 0; k < NUM_MASTERS; k = k + 1) begin : gen_read_mux
            integer m;
            always @(*) begin
                m_read_data[k] = 64'h0;
                // Find which slave this master is connected to
                for (m = 0; m < NUM_SLAVES; m = m + 1) begin
                    if (grant[m] == k) begin
                        m_read_data[k] = s_read_data[m];
                    end
                end
            end
        end
    endgenerate

endmodule
