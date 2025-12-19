import sys
import os

# Adaugam folderul parinte in calea Python (pentru a vedea folderul src)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_sim
from src.line_buffer import LineBuffer

def test_line_buffer_simple():
    # Configurare: Imagini mici de latime 4 pixeli
    WIDTH = 4
    dut = LineBuffer(data_width=8, img_width=WIDTH)
    
    # FIX AICI: Folosim .elaborate() in loc de .elab()
    dut.elaborate() 
    
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()

    print("\nStart Line Buffer Simulation")
    
    # Vom introduce pixeli numerotati 1, 2, 3...
    # Ne asteptam ca la iesire sa vedem coloane verticale
    
    # L1: 1, 2, 3, 4
    # L2: 5, 6, 7, 8
    # L3: 9 ...
    input_pixels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    # Setam receptorul sa fie mereu gata
    dut.send.rdy @= 1
    
    cycle_count = 0
    for p in input_pixels:
        dut.recv.msg @= p
        dut.recv.val @= 1
        dut.sim_tick()
        cycle_count += 1
        
        if dut.send.val:
            # Despachetam iesirea (24 biti total -> 3 pixeli de 8 biti)
            out_bits = dut.send.msg
            p0 = int(out_bits[0:8])   # Pixel curent
            p1 = int(out_bits[8:16])  # Pixel linia anterioara
            p2 = int(out_bits[16:24]) # Pixel 2 linii in urma
            
            print(f"Cycle {cycle_count}: Input={p} -> Output Window=[{p2}, {p1}, {p0}]")
            
            # Verificare automata pentru pixelul 9 (primul din linia 3)
            if p == 9:
                # Verificam daca avem coloana [1, 5, 9]
                assert p1 == 5, f"Expected 5, got {p1}"
                assert p2 == 1, f"Expected 1, got {p2}"
                print(">>> VERIFICATION PASS: Vertical column [1, 5, 9] correctly aligned!")

    print("End Simulation")

if __name__ == "__main__":
    test_line_buffer_simple()