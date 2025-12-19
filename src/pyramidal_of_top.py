from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from src.optical_flow_top import OpticalFlowTop
from src.downsampler import Downsampler
from src.upsampler import Upsampler

class PyramidalOpticalFlow( Component ):
    def construct( s, width=64 ):
        # Interfete Globale
        s.recv_curr = RecvIfcRTL( mk_bits(8) )
        s.recv_prev = RecvIfcRTL( mk_bits(8) )
        s.send_uv   = SendIfcRTL( mk_bits(64) )

        # 1. Componente Nivel Grosier (Coarse)
        s.down_curr = Downsampler( img_width=width )
        s.down_prev = Downsampler( img_width=width )
        
        # Alpha mai mare la nivel coarse pentru stabilitate
        s.of_coarse = OpticalFlowTop( img_width=width//2, alpha=20 )

        # 2. Componenta de legatura
        s.upsampler = Upsampler()

        # 3. Componenta Nivel Fin (Fine)
        # Alpha mai mic la nivel fin pentru detalii
        s.of_fine = OpticalFlowTop( img_width=width, alpha=5 )

        # LOGICA DE CONECTARE (PIPELINE)
        
        # A. SPLITTER INTRARE
        # Trimitem pixelii catre Downsampler SI catre OF_Fine simultan
        # Acceptam date doar daca AMBELE module sunt gata
        
        @update
        def input_splitter_logic():
            # 1. Pixel Curent
            s.down_curr.recv.msg @= s.recv_curr.msg
            s.down_curr.recv.val @= s.recv_curr.val
            
            s.of_fine.recv_curr.msg @= s.recv_curr.msg
            s.of_fine.recv_curr.val @= s.recv_curr.val
            
            # Ready global este AND intre Ready Downsampler si Ready Fine
            s.recv_curr.rdy @= s.down_curr.recv.rdy & s.of_fine.recv_curr.rdy
            
            # 2. Pixel Anterior
            s.down_prev.recv.msg @= s.recv_prev.msg
            s.down_prev.recv.val @= s.recv_prev.val
            
            s.of_fine.recv_prev.msg @= s.recv_prev.msg
            s.of_fine.recv_prev.val @= s.recv_prev.val
            
            s.recv_prev.rdy @= s.down_prev.recv.rdy & s.of_fine.recv_prev.rdy

        # B. Ramura Coarse
        s.down_curr.send //= s.of_coarse.recv_curr
        s.down_prev.send //= s.of_coarse.recv_prev
        
        # Coarse porneste de la zero
        # FIX PENTRU VERILOG: Setam constant 0 si valid 1
        # Nu accesam semnale interne din submodule
        @update
        def coarse_init_logic():
            s.of_coarse.recv_init_uv.msg @= 0
            s.of_coarse.recv_init_uv.val @= 1

        # C. Proiectia Coarse la Upsampler
        s.of_coarse.send_uv //= s.upsampler.recv
        
        # D. Ramura Fine
        # Fine primeste estimarea initiala de la Upsampler
        s.upsampler.send //= s.of_fine.recv_init_uv
        
        # E. Output Final
        s.of_fine.send_uv //= s.send_uv

    def line_trace( s ):
        return f"Out:{s.send_uv.msg[0:32]}"