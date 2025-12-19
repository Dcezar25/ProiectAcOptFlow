
// PyramidalOpticalFlow.v
// Implementation: 2-Level Horn-Schunck Pyramid (64x64 -> 32x32)

`default_nettype none


// MODULE: Downsampler (2x2 Average)

module Downsampler (
  input  wire clk,
  input  wire reset,
  input  wire [7:0] recv_msg,
  input  wire       recv_val,
  output wire       recv_rdy,
  output wire [7:0] send_msg,
  output wire       send_val,
  input  wire       send_rdy
);
  // Simplificare: Bufferare linie si medie 2x2
  // Pentru sinteza eficienta, aici implementam un model comportamental 
  // care simuleaza reducerea debitului de date (1 iesire la 4 intrari)
  
  reg [1:0] cnt_x;
  reg [1:0] cnt_y;
  
  // Logic: Acceptam date mereu, dar validam iesirea doar la final de bloc 2x2
  assign recv_rdy = send_rdy;
  
  // Output logic
  assign send_msg = recv_msg; // Trimitem pixelul curent (sub-sampling simplu pt FPGA mic)
  assign send_val = recv_val && (cnt_x == 1) && (cnt_y == 1);

  always @(posedge clk) begin
    if (reset) begin
      cnt_x <= 0;
      cnt_y <= 0;
    end else if (recv_val && send_rdy) begin
      cnt_x <= cnt_x + 1;
      if (cnt_x == 1) cnt_y <= cnt_y + 1;
    end
  end
endmodule


// MODULE: Upsampler (Scalare x2 si Expandare)

module Upsampler (
  input  wire        clk,
  input  wire        reset,
  input  wire [63:0] recv_msg, // [v, u] de la Coarse
  input  wire        recv_val,
  output wire        recv_rdy,
  output wire [63:0] send_msg, // [v*2, u*2] catre Fine
  output wire        send_val,
  input  wire        send_rdy
);
  assign recv_rdy = send_rdy;
  assign send_val = recv_val;
  
  wire signed [31:0] u_in = recv_msg[31:0];
  wire signed [31:0] v_in = recv_msg[63:32];
  
  // Scalare: Shift Left 1 (Inmultire cu 2)
  wire signed [31:0] u_out = u_in <<< 1;
  wire signed [31:0] v_out = v_in <<< 1;
  
  assign send_msg = {v_out, u_out};
endmodule


// MODULE: LineBuffer (Standard)

module LineBuffer #(parameter WIDTH=64) (
  input  wire clk, input wire reset,
  input  wire [7:0] recv_msg, input wire recv_val, output wire recv_rdy,
  output wire [23:0] send_msg, output wire send_val, input wire send_rdy
);
  reg [7:0] mem1 [0:WIDTH-1];
  reg [7:0] mem2 [0:WIDTH-1];
  reg [31:0] ptr;
  reg [31:0] count;
  reg [7:0] pop;
  assign recv_rdy = send_rdy;
  wire [31:0] ridx = (ptr==0) ? WIDTH-1 : ptr-1;
  assign send_msg = {pop, mem2[ridx], recv_msg};
  assign send_val = recv_val && (count >= WIDTH*2);
  
  always @(posedge clk) begin
    if (reset) begin ptr<=0; count<=0; end
    else if (recv_val && send_rdy) begin
      pop <= mem2[ptr]; mem2[ptr] <= mem1[ptr]; mem1[ptr] <= recv_msg;
      ptr <= (ptr==WIDTH-1) ? 0 : ptr+1;
      count <= count+1;
    end
  end
endmodule


// MODULE: HSCore (With Initial Guess Input)

module HSCore #(parameter ALPHA=10) (
  input wire clk, input wire reset,
  input wire [47:0] recv_grads, input wire recv_grads_val, output wire recv_grads_rdy,
  input wire [63:0] recv_uv,    input wire recv_uv_val,    output wire recv_uv_rdy,
  output wire [63:0] send_uv,   output wire send_uv_val,   input wire send_uv_rdy
);
  localparam signed [31:0] A_SQ = ALPHA*ALPHA;
  assign recv_grads_rdy = send_uv_rdy;
  assign recv_uv_rdy = send_uv_rdy;
  
  wire signed [31:0] ix = {{16{recv_grads[15]}}, recv_grads[15:0]};
  wire signed [31:0] iy = {{16{recv_grads[31]}}, recv_grads[31:16]};
  wire signed [31:0] it = {{16{recv_grads[47]}}, recv_grads[47:32]};
  wire signed [31:0] u0 = recv_uv[31:0];
  wire signed [31:0] v0 = recv_uv[63:32];
  
  wire signed [31:0] den = A_SQ + ix*ix + iy*iy;
  wire signed [31:0] s_den = (den==0) ? 1 : den;
  wire signed [31:0] dt = ix*u0 + iy*v0 + (it <<< 12);
  
  wire signed [31:0] un = u0 - (ix*dt / s_den);
  wire signed [31:0] vn = v0 - (iy*dt / s_den);
  
  assign send_uv = {vn, un};
  assign send_uv_val = recv_grads_val && recv_uv_val;
endmodule


// MODULE: GradientUnit

module GradientUnit (
  input wire clk, input wire reset,
  input wire [23:0] col, input wire col_v, output wire col_r,
  input wire [7:0] prv,  input wire prv_v, output wire prv_r,
  output wire [47:0] gr, output wire gr_v, input wire gr_r
);
  reg [23:0] c0, c1, c2; reg [7:0] p_px;
  assign col_r = gr_r; assign prv_r = gr_r;
  
  wire signed [15:0] p00={8'b0,c0[23:16]}, p02={8'b0,c2[23:16]};
  wire signed [15:0] p10={8'b0,c0[15:8]},  p12={8'b0,c2[15:8]};
  wire signed [15:0] p20={8'b0,c0[7:0]},   p22={8'b0,c2[7:0]};
  wire signed [15:0] p01={8'b0,c1[23:16]}, p21={8'b0,c1[7:0]}, p11={8'b0,c1[15:8]};
  
  wire signed [15:0] ix = (p02 + (p12<<1) + p22) - (p00 + (p10<<1) + p20);
  wire signed [15:0] iy = (p20 + (p21<<1) + p22) - (p00 + (p01<<1) + p02);
  wire signed [15:0] it = p11 - {8'b0, p_px};
  
  assign gr = {it, iy, ix};
  assign gr_v = col_v && prv_v;
  
  always @(posedge clk) if(col_v && gr_r) begin c0<=c1; c1<=c2; c2<=col; p_px<=prv; end
endmodule


// MODULE: OpticalFlowTop (Single Scale)

module OpticalFlowTop #(parameter WIDTH=64, ALPHA=10) (
  input wire clk, input wire reset,
  input wire [7:0] curr, input wire curr_v, output wire curr_r,
  input wire [7:0] prev, input wire prev_v, output wire prev_r,
  input wire [63:0] init, input wire init_v, output wire init_r,
  output wire [63:0] uv, output wire uv_v, input wire uv_r
);
  wire [23:0] lb_gr; wire lb_v, lb_r;
  wire [47:0] gr_hs; wire gr_v, gr_r;
  
  LineBuffer #(WIDTH) lb (clk, reset, curr, curr_v, curr_r, lb_gr, lb_v, lb_r);
  GradientUnit gu (clk, reset, lb_gr, lb_v, lb_r, prev, prev_v, prev_r, gr_hs, gr_v, gr_r);
  
  // HS Core accepts External Init
  HSCore #(ALPHA) hs (clk, reset, gr_hs, gr_v, gr_r, init, init_v, init_r, uv, uv_v, uv_r);
endmodule


// MODULE: PyramidalOpticalFlow (TOP LEVEL)

module PyramidalOpticalFlow (
  input  wire clk,
  input  wire reset,
  input  wire [7:0] recv_curr, input wire recv_curr_val, output wire recv_curr_rdy,
  input  wire [7:0] recv_prev, input wire recv_prev_val, output wire recv_prev_rdy,
  output wire [63:0] send_uv,  output wire send_uv_val,  input wire send_uv_rdy
);
  
  // 1. Splitter Logic
  // Data goes to Downsampler AND Fine Unit
  wire ds_curr_rdy, ds_prev_rdy;
  wire fine_curr_rdy, fine_prev_rdy;
  
  assign recv_curr_rdy = ds_curr_rdy && fine_curr_rdy;
  assign recv_prev_rdy = ds_prev_rdy && fine_prev_rdy;
  
  // 2. Downsamplers
  wire [7:0] ds_curr_msg, ds_prev_msg;
  wire ds_curr_val, ds_prev_val;
  
  Downsampler dc (clk, reset, recv_curr, recv_curr_val, ds_curr_rdy, ds_curr_msg, ds_curr_val, 1'b1);
  Downsampler dp (clk, reset, recv_prev, recv_prev_val, ds_prev_rdy, ds_prev_msg, ds_prev_val, 1'b1);
  
  // 3. Coarse Flow (32x32)
  wire [63:0] coarse_uv; wire coarse_val;
  wire [63:0] zero_uv = 64'b0;
  
  // Coarse module - Init is always valid 0
  OpticalFlowTop #(32, 20) of_coarse (
    .clk(clk), .reset(reset),
    .curr(ds_curr_msg), .curr_v(ds_curr_val), .curr_r(), // Ignore rdy inside pipe for simplicity
    .prev(ds_prev_msg), .prev_v(ds_prev_val), .prev_r(),
    .init(zero_uv),     .init_v(1'b1),        .init_r(),
    .uv(coarse_uv),     .uv_v(coarse_val),    .uv_r(1'b1)
  );
  
  // 4. Upsampler
  wire [63:0] up_uv; wire up_val;
  Upsampler up (clk, reset, coarse_uv, coarse_val, , up_uv, up_val, 1'b1);
  
  // 5. Fine Flow (64x64)
  // Init comes from Upsampler
  OpticalFlowTop #(64, 5) of_fine (
    .clk(clk), .reset(reset),
    .curr(recv_curr), .curr_v(recv_curr_val), .curr_r(fine_curr_rdy),
    .prev(recv_prev), .prev_v(recv_prev_val), .prev_r(fine_prev_rdy),
    .init(up_uv),     .init_v(up_val),        .init_r(), 
    .uv(send_uv),     .uv_v(send_uv_val),     .uv_r(send_uv_rdy)
  );

endmodule