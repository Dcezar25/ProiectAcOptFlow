from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

class HSCore( Component ):
    def construct( s, alpha=10 ):
        FP_SHIFT = 12
        s.ALPHA_SQ = Wire( mk_bits(32) )
        s.ALPHA_SQ //= (alpha * alpha) 

        s.recv_grads = RecvIfcRTL( mk_bits(48) )
        s.recv_uv    = RecvIfcRTL( mk_bits(64) ) # Initial Guess
        s.send_uv    = SendIfcRTL( mk_bits(64) )
        
        # Debugging signals
        s.dbg_denom = Wire( mk_bits(32) )
        
        # Declaram explicit firul pentru numitorul sigur
        s.denom_safe = Wire( mk_bits(32) )

        @update
        def math_logic():
            s.recv_grads.rdy @= s.send_uv.rdy
            s.recv_uv.rdy    @= s.send_uv.rdy
            
            # 1. Extragere Valori Raw (Bits)
            raw_ix = s.recv_grads.msg[0:16]
            raw_iy = s.recv_grads.msg[16:32]
            raw_it = s.recv_grads.msg[32:48]
            
            raw_u_init = s.recv_uv.msg[0:32]
            raw_v_init = s.recv_uv.msg[32:64]
            
            # 2. Extensie de Semn
            ix = sext(raw_ix, 32)
            iy = sext(raw_iy, 32)
            it = sext(raw_it, 32)
            
            u_init = raw_u_init
            v_init = raw_v_init
            
            # 3. Calcule Matematice
            denom = s.ALPHA_SQ + (ix * ix) + (iy * iy)
            
            # Protectie la impartire prin zero
            if denom == 0: 
                s.denom_safe @= 1
            else:
                s.denom_safe @= denom
            
            s.dbg_denom @= s.denom_safe
            
            # Data Term
            term_it = it << FP_SHIFT
            data_term = (ix * u_init) + (iy * v_init) + term_it
            
            # Calcul Update
            # FIX: Folosim // (diviziune intreaga) in loc de / 
            num_u = ix * data_term
            update_u = num_u // s.denom_safe
            
            num_v = iy * data_term
            update_v = num_v // s.denom_safe
            
            # Rezultat Final
            u_new = u_init - update_u
            v_new = v_init - update_v
            
            # Impachetare
            s.send_uv.msg @= concat( v_new, u_new )
            s.send_uv.val @= s.recv_grads.val & s.recv_uv.val

    def line_trace( s ):
        return f"D:{s.dbg_denom} U:{s.send_uv.msg[0:32]}"