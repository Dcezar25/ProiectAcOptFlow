import sys
import os
import numpy as np

# Setup cai pentru importuri
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../golden_model')))

from pymtl3 import *
from src.pyramidal_of_top import PyramidalOpticalFlow
from generate_test_data import create_moving_square

def test_pyramid_system():
    # 1. Generare Date (Patrat 64x64)
    WIDTH = 64
    im1, im2 = create_moving_square(size=WIDTH, shift_x=1, shift_y=0)
    
    pixels_curr = im2.flatten()
    pixels_prev = im1.flatten()
    
    # 2. Initializare Hardware
    print("Initializing Pyramidal Optical Flow...")
    dut = PyramidalOpticalFlow( width=WIDTH )
    dut.elaborate()
    
    # Nu mai activam textwave=True, rulam simplu
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    
    print("Start Simulation...")
    
    dut.send_uv.rdy @= 1
    output_u = []
    
    total_pixels = len(pixels_curr)
    curr_idx = 0
    prev_idx = 0
    results_collected = 0
    
    # Timeout
    max_cycles = total_pixels + 4000 
    
    for cycle in range(max_cycles):
        # 1. Alimentare Input
        if curr_idx < total_pixels:
            dut.recv_curr.msg @= int(pixels_curr[curr_idx])
            dut.recv_curr.val @= 1
        else:
            dut.recv_curr.val @= 0 
            
        if prev_idx < total_pixels:
            dut.recv_prev.msg @= int(pixels_prev[prev_idx])
            dut.recv_prev.val @= 1
        else:
            dut.recv_prev.val @= 0
            
        dut.sim_tick()
        
        # 2. Gestionare indecsi (Handshake)
        if dut.recv_curr.val and dut.recv_curr.rdy:
            curr_idx += 1
        if dut.recv_prev.val and dut.recv_prev.rdy:
            prev_idx += 1
            
        # 3. Colectare Output
        if dut.send_uv.val:
            raw_u = int(dut.send_uv.msg[0:32])
            
            # Conversie Signed 32-bit
            if raw_u > 2147483647: raw_u -= 4294967296
            
            # Conversie Fixed-Point Q4.12 la Float
            u_float = raw_u / 4096.0
            output_u.append(u_float)
            results_collected += 1
            
        if results_collected >= total_pixels:
            break
            
    print(f"Simulation finished. Processed {results_collected} pixels.")
    
    # 4. Verificare Rezultate
    u_arr = np.array(output_u)
    
    if len(u_arr) > 0:
        max_u = np.max(u_arr)
        print(f"Max U detected: {max_u:.4f}")
        
        # Verificam daca am detectat miscarea corect (pentru piramida trebuie sa fie > 0.6)
        if max_u > 0.6:
            print("SUCCESS Pyramidal approach works")
        else:
            print("WARNING Magnitude low")
    else:
        print("ERROR No output collected")

if __name__ == "__main__":
    test_pyramid_system()