from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

class Upsampler( Component ):
    def construct( s ):
        s.recv = RecvIfcRTL( mk_bits(64) ) 
        s.send = SendIfcRTL( mk_bits(64) )

        # FIX: Am redenumit 'logic' in 'comb_logic'
        @update
        def comb_logic():
            s.recv.rdy @= s.send.rdy
            
            u_coarse = s.recv.msg[0:32]
            v_coarse = s.recv.msg[32:64]
            
            u_scaled = u_coarse << 1
            v_scaled = v_coarse << 1
            
            s.send.msg @= concat( v_scaled, u_scaled )
            s.send.val @= s.recv.val