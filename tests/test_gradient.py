import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymtl3 import *
from src.gradient_unit import GradientUnit

def test_gradient_vertical_edge():
    dut = GradientUnit()
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()

    print("\nStart Gradient Simulation")
    dut.send_grad.rdy @= 1
    
    # Definim constantele ca Bits24 pentru siguranta, dar python le poate vedea ca int
    col_zero = Bits24(0)
    col_val  = concat( Bits8(100), Bits8(100), Bits8(100) ) # 3 pixeli de 100
    
    inputs = [col_zero, col_zero, col_val, col_val, col_val]
    
    cycle = 0
    for col in inputs:
        dut.recv_col.msg @= col
        dut.recv_col.val @= 1
        
        
        # Shiftam la dreapta cu 8 biti si luam ultimii 8 biti (Masca 0xFF)
        # Asta este echivalentul lui col[8:16] dar functioneaza si pe int si pe Bits
        mid_val = (int(col) >> 8) & 0xFF
        
        dut.recv_prev.msg @= mid_val
        dut.recv_prev.val @= 1
        
        dut.sim_tick()
        cycle += 1
        
        if dut.send_grad.val and cycle > 2:
            # Despachetare: [It(47:32), Iy(31:16), Ix(15:0)]
            out = dut.send_grad.msg
            ix = int(out[0:16])
            iy = int(out[16:32])
            it = int(out[32:48])
            
            # Conversie manuala in Signed 16-bit
            if ix > 32767: ix -= 65536
            if iy > 32767: iy -= 65536
            
            print(f"Cycle {cycle}: Ix={ix}, Iy={iy}, It={it}")
            
            # VERIFICARE:
            # La ciclul 4, Ix trebuie sa fie pozitiv (trecere 0 -> 100)
            if cycle == 4:
                # Kernel X [-1 0 1]: (Dreapta - Stanga)
                # Stanga=0, Dreapta=100 => Ix = +400 (datorita ponderilor 1 si 2)
                if ix > 0:
                    print(f">>> VERIFICATION PASS: Edge detected! Ix={ix} (Expected positive)")
                else:
                    print(f">>> FAIL: Ix should be positive, got {ix}")

    print("End Simulation")

if __name__ == "__main__":
    test_gradient_vertical_edge()