// Automatically generated by PRGA's RTL generator
module {{ module.name }} (
    input wire [0:0] clk,
    input wire [0:0] D,
    output reg [0:0] Q
    );

    always @(posedge clk[0]) begin
        Q   <=  D;
    end

endmodule
