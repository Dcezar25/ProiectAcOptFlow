import sys
import os

# Adăugăm folderul rădăcină în calea Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymtl3 import *
from src.downsampler import Downsampler
from src.upsampler import Upsampler

# 1. Test pentru Downsampler
def test_downsampler_simple():
    print("\n--- Testing Downsampler (64x64 -> 32x32)")
    WIDTH = 4 # Folosim o lățime mică pentru test (4x4 -> 2x2)
    dut = Downsampler( img_width=WIDTH )
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()

    # Trimitem un bloc de 2x2 pixeli cu valorile [100, 100, 100, 100]
    # Media ar trebui să fie 100.
    # Trimitem 2 rânduri complete pentru a genera un singur pixel de ieșire
    
    # Rândul 0: [100, 100, 50, 50]
    # Rândul 1: [100, 100, 50, 50]
    # Rezultat așteptat: Două valori la ieșire: 100 (media primului bloc 2x2) și 50 (al doilea)
    
    pixels = [100, 100, 50, 50, 
              100, 100, 50, 50]
    
    dut.send.rdy @= 1
    results = []

    for p in pixels:
        dut.recv.msg @= p
        dut.recv.val @= 1
        dut.sim_tick()
        if dut.send.val:
            results.append( int(dut.send.msg) )

    print(f"Input 4x2 pixels, Output: {results}")
    
    # Verificare: Din 8 pixeli (2 rânduri de 4), trebuie să iasă 2 pixeli (media coloanelor 2x2)
    assert len(results) == 2
    assert results[0] == 100
    assert results[1] == 50
    print(">>> Downsampler Test PASS!")

# 2. Test pentru Upsampler
def test_upsampler_scaling():
    print("\n--- Testing Upsampler (Scale x2)")
    dut = Upsampler()
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()

    dut.send.rdy @= 1
    
    # Trimitem u = 1.0 (4096 în Q4.12) și v = 0.5 (2048 în Q4.12)
    u_in = 4096
    v_in = 2048
    dut.recv.msg @= concat( Bits32(v_in), Bits32(u_in) )
    dut.recv.val @= 1
    
    dut.sim_tick()
    
    if dut.send.val:
        u_out = int(dut.send.msg[0:32])
        v_out = int(dut.send.msg[32:64])
        
        print(f"Input: u={u_in}, v={v_in}")
        print(f"Output: u={u_out}, v={v_out}")
        
        # Trebuie să fie dublate: u=8192, v=4096
        assert u_out == u_in * 2
        assert v_out == v_in * 2
        print(">>> Upsampler Test PASS!")

if __name__ == "__main__":
    test_downsampler_simple()
    test_upsampler_scaling()