from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL
from src.line_buffer import LineBuffer
from src.gradient_unit import GradientUnit
from src.hs_core import HSCore

class OpticalFlowTop( Component ):
    def construct( s, img_width=64, alpha=10 ):
        # Interfete Externe
        s.recv_curr = RecvIfcRTL( mk_bits(8) )
        s.recv_prev = RecvIfcRTL( mk_bits(8) )
        
        # Port pentru Initial Guess (de la Piramida)
        s.recv_init_uv = RecvIfcRTL( mk_bits(64) )
        
        s.send_uv   = SendIfcRTL( mk_bits(64) )

        # Instantiere Module
        s.line_buffer = LineBuffer( data_width=8, img_width=img_width )
        s.grad_unit   = GradientUnit()
        s.hs_core     = HSCore( alpha=alpha )

        # Conectare Pipeline
        s.recv_curr //= s.line_buffer.recv
        s.line_buffer.send //= s.grad_unit.recv_col
        s.recv_prev //= s.grad_unit.recv_prev
        s.grad_unit.send_grad //= s.hs_core.recv_grads
        
        # LOGICA SELECTIE INIT UV (Prioritate Externa)
        # Conectam direct portul extern la intrarea HS Core.
        # Daca acest modul este folosit ca 'Coarse' (nivelul 1), vom lega 0 la recv_init_uv din afara.
        # Daca este folosit ca 'Fine' (nivelul 0), vom lega Upsampler-ul aici.
        
        s.recv_init_uv //= s.hs_core.recv_uv
        
        s.hs_core.send_uv //= s.send_uv

    def line_trace( s ):
        return f"In:{s.recv_curr.msg} > {s.hs_core.line_trace()}"