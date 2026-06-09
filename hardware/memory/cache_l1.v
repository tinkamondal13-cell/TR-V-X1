// Triton L1 Cache Subsystem
// Dual-port L1 cache: Instruction and Data

module triton_l1_cache #(
    parameter CACHE_SIZE = 16384,    // 16 KB
    parameter LINE_SIZE = 64,        // 64 trits = 96 bits
    parameter ASSOCIATIVITY = 4,
    parameter ADDR_WIDTH = 32
) (
    input                              clk,
    input                              reset_n,
    
    // Instruction cache port
    input  [ADDR_WIDTH-1:0]            i_addr,
    output reg [(LINE_SIZE*2)-1:0]     i_data,
    output reg                         i_hit,
    input                              i_valid,
    
    // Data cache port
    input  [ADDR_WIDTH-1:0]            d_addr,
    input  [(LINE_SIZE*2)-1:0]         d_write_data,
    output reg [(LINE_SIZE*2)-1:0]     d_read_data,
    output reg                         d_hit,
    input                              d_read_enable,
    input                              d_write_enable,
    
    // Memory interface
    output reg                         mem_req,
    output reg [ADDR_WIDTH-1:0]        mem_addr,
    input  [(LINE_SIZE*2)-1:0]         mem_data,
    input                              mem_valid
);

    // Cache parameters
    localparam NUM_SETS = CACHE_SIZE / (LINE_SIZE * ASSOCIATIVITY);
    localparam SET_BITS = $clog2(NUM_SETS);
    localparam TAG_BITS = ADDR_WIDTH - SET_BITS - 6;  // 6 bits for offset
    localparam OFFSET_BITS = 6;

    // Cache tag array
    reg [TAG_BITS-1:0]         i_tags   [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    reg [TAG_BITS-1:0]         d_tags   [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    
    // Cache data array
    reg [(LINE_SIZE*2)-1:0]    i_data_array [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    reg [(LINE_SIZE*2)-1:0]    d_data_array [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    
    // Valid bits
    reg                        i_valid_bits [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    reg                        d_valid_bits [0:NUM_SETS-1][0:ASSOCIATIVITY-1];
    
    // LRU replacement policy
    reg [ASSOCIATIVITY-1:0]    i_lru [0:NUM_SETS-1];
    reg [ASSOCIATIVITY-1:0]    d_lru [0:NUM_SETS-1];

    // Address decomposition
    wire [SET_BITS-1:0]        i_set = i_addr[SET_BITS+OFFSET_BITS-1:OFFSET_BITS];
    wire [TAG_BITS-1:0]        i_tag = i_addr[ADDR_WIDTH-1:SET_BITS+OFFSET_BITS];
    
    wire [SET_BITS-1:0]        d_set = d_addr[SET_BITS+OFFSET_BITS-1:OFFSET_BITS];
    wire [TAG_BITS-1:0]        d_tag = d_addr[ADDR_WIDTH-1:SET_BITS+OFFSET_BITS];

    // Initialization
    initial begin
        integer i, j;
        for (i = 0; i < NUM_SETS; i = i + 1) begin
            for (j = 0; j < ASSOCIATIVITY; j = j + 1) begin
                i_valid_bits[i][j] = 1'b0;
                d_valid_bits[i][j] = 1'b0;
                i_lru[i] = {ASSOCIATIVITY{1'b0}};
                d_lru[i] = {ASSOCIATIVITY{1'b0}};
            end
        end
    end

    // Instruction cache lookup
    always @(*) begin
        integer k;
        i_hit = 1'b0;
        i_data = 128'h0;
        
        for (k = 0; k < ASSOCIATIVITY; k = k + 1) begin
            if (i_valid_bits[i_set][k] && (i_tags[i_set][k] == i_tag)) begin
                i_hit = 1'b1;
                i_data = i_data_array[i_set][k];
            end
        end
    end

    // Data cache lookup
    always @(*) begin
        integer k;
        d_hit = 1'b0;
        d_read_data = 128'h0;
        
        for (k = 0; k < ASSOCIATIVITY; k = k + 1) begin
            if (d_valid_bits[d_set][k] && (d_tags[d_set][k] == d_tag)) begin
                d_hit = 1'b1;
                d_read_data = d_data_array[d_set][k];
            end
        end
    end

    // Cache update on write
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            mem_req <= 1'b0;
        end else begin
            if (d_write_enable && d_hit) begin
                // Write hit - update cache
                d_data_array[d_set][0] <= d_write_data;
            end else if (d_write_enable && !d_hit) begin
                // Write miss - request from memory
                mem_req <= 1'b1;
                mem_addr <= d_addr;
            end else if (mem_valid) begin
                // Memory response - fill cache
                mem_req <= 1'b0;
                d_data_array[d_set][d_lru[d_set]] <= mem_data;
                d_tags[d_set][d_lru[d_set]] <= d_tag;
                d_valid_bits[d_set][d_lru[d_set]] <= 1'b1;
            end
        end
    end

endmodule
