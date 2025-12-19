from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

class Downsampler( Component ):
    def construct( s, img_width=64 ):
        s.recv = RecvIfcRTL( mk_bits(8) )
        s.send = SendIfcRTL( mk_bits(8) )

        s.img_width = img_width
        
        s.line_buffer = [ Wire( mk_bits(8) ) for _ in range(img_width) ]
        
        # Pointer pe 6 biti pentru 64 elemente
        s.ptr = Wire( mk_bits(6) ) 
        
        s.row_odd = Wire( mk_bits(1) ) 
        s.col_odd = Wire( mk_bits(1) ) 

        # FIX: Am redenumit 'logic' in 'seq_logic' pentru a evita conflictul SystemVerilog
        @update_ff
        def seq_logic():
            if s.reset:
                s.ptr <<= 0
                s.row_odd <<= 0
                s.col_odd <<= 0
            elif s.recv.val & s.send.rdy:
                if s.ptr == s.img_width - 1:
                    s.ptr <<= 0
                    s.row_odd <<= ~s.row_odd
                else:
                    s.ptr <<= s.ptr + 1
                
                s.col_odd <<= ~s.col_odd
                s.line_buffer[s.ptr] <<= s.recv.msg

        @update
        def output_logic():
            s.recv.rdy @= s.send.rdy
            
            avg = (zext(s.recv.msg, 9) + zext(s.line_buffer[s.ptr], 9)) >> 1
            s.send.msg @= avg[0:8]
            
            s.send.val @= s.recv.val & s.row_odd & s.col_odd