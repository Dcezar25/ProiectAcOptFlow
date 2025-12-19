from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

class GradientUnit( Component ):
    def construct( s ):
        # Input 1: Coloana curenta de 3 pixeli
        s.recv_col = RecvIfcRTL( mk_bits(24) )
        
        # Input 2: Pixelul din cadrul anterior
        s.recv_prev = RecvIfcRTL( mk_bits(8) )
        
        # Output: Ix, Iy, It (3x 16 biti = 48 biti)
        s.send_grad = SendIfcRTL( mk_bits(48) )

        # Registre pentru Fereastra 3x3
        s.col_0 = Wire( mk_bits(24) )
        s.col_1 = Wire( mk_bits(24) )
        s.col_2 = Wire( mk_bits(24) )

        # Pixelul central din cadrul anterior
        s.prev_frame_pixel = Wire( mk_bits(16) )

        @update_ff
        def shift_window_logic():
            if s.reset:
                s.col_0 <<= 0
                s.col_1 <<= 0
                s.col_2 <<= 0
            # FIX: Folosim & in loc de and
            elif s.recv_col.val & s.send_grad.rdy:
                # Shiftam coloanele spre stanga
                s.col_0 <<= s.col_1
                s.col_1 <<= s.col_2
                s.col_2 <<= s.recv_col.msg
                
                # Memoram pixelul prev
                s.prev_frame_pixel <<= zext(s.recv_prev.msg, 16)

        @update
        def calculation_logic():
            # Ready logic
            s.recv_col.rdy  @= s.send_grad.rdy
            s.recv_prev.rdy @= s.send_grad.rdy
            
            # 1. Extragem pixelii din fereastra 3x3
            # Coloana Stanga (0)
            p00 = zext(s.col_0[16:24], 16) # Sus-Stanga
            p10 = zext(s.col_0[ 8:16], 16) # Mij-Stanga
            p20 = zext(s.col_0[ 0: 8], 16) # Jos-Stanga
            
            # Coloana Mijloc (1)
            p01 = zext(s.col_1[16:24], 16) # Sus-Mij
            p11 = zext(s.col_1[ 8:16], 16) # Centru
            p21 = zext(s.col_1[ 0: 8], 16) # Jos-Mij
            
            # Coloana Dreapta (2)
            p02 = zext(s.col_2[16:24], 16) # Sus-Dreapta
            p12 = zext(s.col_2[ 8:16], 16) # Mij-Dreapta
            p22 = zext(s.col_2[ 0: 8], 16) # Jos-Dreapta
            
            # 2. Calcul Sobel X
            # Ix = (p02 + 2*p12 + p22) - (p00 + 2*p10 + p20)
            pos_term_x = p02 + (p12 << 1) + p22
            neg_term_x = p00 + (p10 << 1) + p20
            ix_val = pos_term_x - neg_term_x
            
            # 3. Calcul Sobel Y
            # Iy = (p20 + 2*p21 + p22) - (p00 + 2*p01 + p02)
            pos_term_y = p20 + (p21 << 1) + p22
            neg_term_y = p00 + (p01 << 1) + p02
            iy_val = pos_term_y - neg_term_y
            
            # 4. Calcul Derivata Temporala (It)
            it_val = p11 - s.prev_frame_pixel
            
            # 5. Output [It, Iy, Ix]
            s.send_grad.msg @= concat( it_val, iy_val, ix_val )
            
            # Valid logic
            s.send_grad.val @= s.recv_col.val & s.recv_prev.val

    def line_trace( s ):
        return f"Ix:{s.send_grad.msg[0:16]} Iy:{s.send_grad.msg[16:32]}"