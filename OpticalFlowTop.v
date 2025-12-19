
// OpticalFlowTop.v
// Implementation: Horn-Schunck Optical Flow (PyMTL3 Equivalent)

`default_nettype none


// Module: LineBuffer

module LineBuffer (
  input  wire        clk,
  input  wire        reset,
  input  wire [7:0]  recv_msg,
  input  wire        recv_val,
  output wire        recv_rdy,
  output wire [23:0] send_msg,
  output wire        send_val,
  input  wire        send_rdy
);
  localparam IMG_WIDTH = 64;
  reg [7:0] line_mem_1 [0:IMG_WIDTH-1];
  reg [7:0] line_mem_2 [0:IMG_WIDTH-1];
  reg [31:0] ptr;
  reg [31:0] count;
  reg [7:0]  val_popped;

  assign recv_rdy = send_rdy;

  // Read Logic
  wire [31:0] r_idx = (ptr == 0) ? (IMG_WIDTH - 1) : (ptr - 1);
  wire [7:0] p0 = recv_msg;        // Current
  wire [7:0] p1 = line_mem_2[r_idx]; // Mid
  wire [7:0] p2 = val_popped;      // Top
  assign send_msg = {p2, p1, p0};
  assign send_val = recv_val && (count >= (IMG_WIDTH * 2));

  // Write Logic
  always @(posedge clk) begin
    if (reset) begin
      ptr <= 0; count <= 0; val_popped <= 0;
    end else if (recv_val && send_rdy) begin
      val_popped <= line_mem_2[ptr];
      line_mem_2[ptr] <= line_mem_1[ptr];
      line_mem_1[ptr] <= recv_msg;
      
      if (ptr == IMG_WIDTH - 1) ptr <= 0;
      else ptr <= ptr + 1;
      count <= count + 1;
    end
  end
endmodule


// Module: GradientUnit

module GradientUnit (
  input  wire        clk,
  input  wire        reset,
  input  wire [23:0] recv_col_msg,
  input  wire        recv_col_val,
  output wire        recv_col_rdy,
  input  wire [7:0]  recv_prev_msg,
  input  wire        recv_prev_val,
  output wire        recv_prev_rdy,
  output wire [47:0] send_grad_msg,
  output wire        send_grad_val,
  input  wire        send_grad_rdy
);
  reg [23:0] col_0, col_1, col_2;
  reg [15:0] prev_pixel;
  
  assign recv_col_rdy = send_grad_rdy;
  assign recv_prev_rdy = send_grad_rdy;

  // Sobel Kernel Logic
  wire signed [15:0] p00 = {8'b0, col_0[23:16]}; wire signed [15:0] p02 = {8'b0, col_2[23:16]};
  wire signed [15:0] p10 = {8'b0, col_0[15:8]};  wire signed [15:0] p12 = {8'b0, col_2[15:8]};
  wire signed [15:0] p20 = {8'b0, col_0[7:0]};   wire signed [15:0] p22 = {8'b0, col_2[7:0]};
  wire signed [15:0] p01 = {8'b0, col_1[23:16]}; wire signed [15:0] p21 = {8'b0, col_1[7:0]};
  wire signed [15:0] p11 = {8'b0, col_1[15:8]};

  wire signed [15:0] ix = (p02 + (p12 <<< 1) + p22) - (p00 + (p10 <<< 1) + p20);
  wire signed [15:0] iy = (p20 + (p21 <<< 1) + p22) - (p00 + (p01 <<< 1) + p02);
  wire signed [15:0] it = p11 - prev_pixel;

  assign send_grad_msg = {it, iy, ix};
  assign send_grad_val = recv_col_val && recv_prev_val;

  always @(posedge clk) begin
    if (reset) begin
      col_0 <= 0; col_1 <= 0; col_2 <= 0; prev_pixel <= 0;
    end else if (recv_col_val && send_grad_rdy) begin
      col_0 <= col_1; col_1 <= col_2; col_2 <= recv_col_msg;
      prev_pixel <= {8'b0, recv_prev_msg};
    end
  end
endmodule


// Module: HSCore (Arithmetic Core)

module HSCore (
  input  wire        clk,
  input  wire        reset,
  input  wire [47:0] recv_grads_msg,
  input  wire        recv_grads_val,
  output wire        recv_grads_rdy,
  input  wire [63:0] recv_uv_msg,
  input  wire        recv_uv_val,
  output wire        recv_uv_rdy,
  output wire [63:0] send_uv_msg,
  output wire        send_uv_val,
  input  wire        send_uv_rdy
);
  localparam signed [31:0] ALPHA_SQ = 100;
  
  assign recv_grads_rdy = send_uv_rdy;
  assign recv_uv_rdy = send_uv_rdy;

  wire signed [31:0] ix = {{16{recv_grads_msg[15]}}, recv_grads_msg[15:0]};
  wire signed [31:0] iy = {{16{recv_grads_msg[31]}}, recv_grads_msg[31:16]};
  wire signed [31:0] it = {{16{recv_grads_msg[47]}}, recv_grads_msg[47:32]};
  wire signed [31:0] u_avg = recv_uv_msg[31:0];
  wire signed [31:0] v_avg = recv_uv_msg[63:32];

  wire signed [31:0] denom = ALPHA_SQ + (ix*ix) + (iy*iy);
  wire signed [31:0] s_denom = (denom == 0) ? 1 : denom;
  wire signed [31:0] data_term = (ix*u_avg) + (iy*v_avg) + (it <<< 12);

  wire signed [31:0] u_new = u_avg - ((ix * data_term) / s_denom);
  wire signed [31:0] v_new = v_avg - ((iy * data_term) / s_denom);

  assign send_uv_msg = {v_new, u_new};
  assign send_uv_val = recv_grads_val && recv_uv_val;
endmodule


// Module: OpticalFlowTop

module OpticalFlowTop (
  input  wire        clk,
  input  wire        reset,
  input  wire [7:0]  recv_curr_msg,
  input  wire        recv_curr_val,
  output wire        recv_curr_rdy,
  input  wire [7:0]  recv_prev_msg,
  input  wire        recv_prev_val,
  output wire        recv_prev_rdy,
  output wire [63:0] send_uv_msg,
  output wire        send_uv_val,
  input  wire        send_uv_rdy
);
  wire [23:0] lb_grad_msg; wire lb_grad_val, lb_grad_rdy;
  wire [47:0] grad_hs_msg; wire grad_hs_val, grad_hs_rdy;

  LineBuffer lb (
    .clk(clk), .reset(reset),
    .recv_msg(recv_curr_msg), .recv_val(recv_curr_val), .recv_rdy(recv_curr_rdy),
    .send_msg(lb_grad_msg), .send_val(lb_grad_val), .send_rdy(lb_grad_rdy)
  );

  GradientUnit grad (
    .clk(clk), .reset(reset),
    .recv_col_msg(lb_grad_msg), .recv_col_val(lb_grad_val), .recv_col_rdy(lb_grad_rdy),
    .recv_prev_msg(recv_prev_msg), .recv_prev_val(recv_prev_val), .recv_prev_rdy(recv_prev_rdy),
    .send_grad_msg(grad_hs_msg), .send_grad_val(grad_hs_val), .send_grad_rdy(grad_hs_rdy)
  );

  HSCore hs (
    .clk(clk), .reset(reset),
    .recv_grads_msg(grad_hs_msg), .recv_grads_val(grad_hs_val), .recv_grads_rdy(grad_hs_rdy),
    .recv_uv_msg(64'd0), .recv_uv_val(grad_hs_val), .recv_uv_rdy(),
    .send_uv_msg(send_uv_msg), .send_uv_val(send_uv_val), .send_uv_rdy(send_uv_rdy)
  );
endmodule