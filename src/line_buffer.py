from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL
import math

class LineBuffer( Component ):
    def construct( s, data_width=8, img_width=64 ):
        # Interfete
        s.recv = RecvIfcRTL( mk_bits(data_width) )
        s.send = SendIfcRTL( mk_bits(data_width * 3) )

        s.IMG_WIDTH = img_width
        
        # Componente Interne
        s.line_mem_1 = [ Wire( mk_bits(data_width) ) for _ in range(img_width) ]
        s.line_mem_2 = [ Wire( mk_bits(data_width) ) for _ in range(img_width) ]
        
        # Registru special: Salveaza valoarea care "cade" din bufferul 2
        s.val_popped = Wire( mk_bits(data_width) )

        # FIX: Calculam exact cati biti ne trebuie pentru pointer
        # Pentru 64 pixeli -> log2(64) = 6 biti. 
        # Astfel evitam eroarea "Index too wide".
        ptr_bits = int(math.ceil(math.log2(img_width)))
        s.ptr = Wire( mk_bits(ptr_bits) ) 
        
        s.count = Wire( mk_bits(32) )

        @update_ff
        def sequential_logic():
            if s.reset:
                s.ptr <<= 0
                s.count <<= 0
                s.val_popped <<= 0
            # FIX: Folosim & in loc de and
            elif s.recv.val & s.send.rdy:
                # FIX: Eliminam int(). Folosim semnalul direct.
                idx = s.ptr
                
                # 1. SALVAM VECHILE VALORI
                s.val_popped <<= s.line_mem_2[idx]
                
                # 2. SHIFTAM DATELE
                s.line_mem_2[idx] <<= s.line_mem_1[idx]
                s.line_mem_1[idx] <<= s.recv.msg
                
                # 3. ACTUALIZAM POINTERII
                if s.ptr == s.IMG_WIDTH - 1:
                    s.ptr <<= 0
                else:
                    s.ptr <<= s.ptr + 1
                
                s.count <<= s.count + 1

        @update
        def output_logic():
            s.recv.rdy @= s.send.rdy
            
            # CALCUL INDEX CITIRE
            # FIX: Eliminam int()
            # Logica de wrap-around pentru pointer circular
            r_idx = s.ptr
            if s.ptr == 0:
                r_idx = s.IMG_WIDTH - 1
            else:
                r_idx = s.ptr - 1
            
            # CONSTRUIRE FEREASTRA
            p0 = s.recv.msg
            p1 = s.line_mem_2[r_idx]
            p2 = s.val_popped
            
            s.send.msg @= concat( p2, p1, p0 )
            
            # Valid dupa ce avem 2 linii pline
            # Folosim & in loc de and
            s.send.val @= s.recv.val & (s.count >= (s.IMG_WIDTH * 2))

    def line_trace( s ):
        return f"In:{s.recv.msg} Out:{s.send.msg}"