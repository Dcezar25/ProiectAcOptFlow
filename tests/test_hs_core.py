import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymtl3 import *
from src.hs_core import HSCore

def test_hs_math_sanity():
    # alpha = 0 pentru test simplu (fara regularizare)
    dut = HSCore(alpha=0)
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()

    print("\nStart Horn-Schunck Math Core Test")
    dut.send_uv.rdy @= 1
    
    # Cazul 1: Miscare simpla pe X
    # Ix = 10, Iy = 0, It = -10 (Integer)
    # Asteptam ca algoritmul sa gaseasca u = 1.0
    # Ecuatia: 10*u - 10 = 0 -> u = 1
    
    ix = Bits16(10)
    iy = Bits16(0)
    # It este negativ (-10). In Two's complement pe 16 biti:
    it = Bits16( -10 & 0xFFFF ) 
    
    dut.recv_grads.msg @= concat( it, iy, ix )
    
    # Input initial u, v = 0 (Fixed Point)
    dut.recv_uv.msg @= 0
    
    # Valid
    dut.recv_grads.val @= 1
    dut.recv_uv.val    @= 1
    
    dut.sim_tick()
    dut.sim_tick()
    
    if dut.send_uv.val:
        u_out = int(dut.send_uv.msg[0:32])
        v_out = int(dut.send_uv.msg[32:64])
        
        # Conversie din unsigned inapoi in signed 32bit daca e cazul
        if u_out > 2147483647: u_out -= 4294967296
        
        print(f"Input: Ix=10, It=-10, U_avg=0")
        print(f"Output Raw: {u_out} (Q4.12 Fixed Point)")
        print(f"Output Float: {u_out / 4096.0}")
        
        # Verificare
        # Asteptam 1.0 (4096). Acceptam o mica eroare de rotunjire
        assert 4000 < u_out < 4200, f"Expected approx 4096 (1.0), got {u_out}"
        print(">>> VERIFICATION PASS: Calculated u=1.0 correctly!")

if __name__ == "__main__":
    test_hs_math_sanity()