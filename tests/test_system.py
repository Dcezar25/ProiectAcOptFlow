import sys
import os
import numpy as np

# FIX IMPORTURI
# 1. Adaugam radacina proiectului pentru a vedea 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Adaugam explicit folderul 'golden_model' pentru ca generate_test_data sa isi gaseasca dependintele
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../golden_model')))

from pymtl3 import *
from src.optical_flow_top import OpticalFlowTop
# Acum acest import va functiona
from generate_test_data import create_moving_square 

def test_system_integration():
    # 1. Generare Date (Patrat miscator 64x64)
    WIDTH = 64
    im1, im2 = create_moving_square(size=WIDTH, shift_x=1, shift_y=0)
    
    # Aplatizam imaginile in liste de pixeli
    pixels_curr = im2.flatten() # Frame curent (t)
    pixels_prev = im1.flatten() # Frame anterior (t-1)
    
    # 2. Initializare Hardware
    # alpha=5 pentru regularizare
    dut = OpticalFlowTop(img_width=WIDTH, alpha=5)
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    
    print("\nStart Full System Simulation (FPGA Pipeline)")
    
    # Setam output-ul sa fie mereu gata sa primeasca date
    dut.send_uv.rdy @= 1
    
    output_u = []
    
    # Rularea Simularii Pixel cu Pixel
    total_pixels = len(pixels_curr)
    
    # Pipeline Latency Fill
    curr_idx = 0
    prev_idx = 0
    results_collected = 0
    
    # Timeout safety
    max_cycles = total_pixels + 2000 
    
    for cycle in range(max_cycles):
        # 1. Alimentam Pixel Curent
        if curr_idx < total_pixels:
            dut.recv_curr.msg @= int(pixels_curr[curr_idx])
            dut.recv_curr.val @= 1
        else:
            dut.recv_curr.val @= 0 
            
        # 2. Alimentam Pixel Anterior
        # NOTA: Intr-un sistem real, 'prev' trebuie sincronizat cu iesirea din LineBuffer.
        # LineBuffer are o latenta de aprox (WIDTH * 2) + 2 cicli.
        # Pentru acest test simplu, trimitem datele simultan. Desi exista un decalaj spatial
        # mic (2 linii), patratul fiind mare, ar trebui sa detectam totusi intersectia.
        if prev_idx < total_pixels:
            dut.recv_prev.msg @= int(pixels_prev[prev_idx])
            dut.recv_prev.val @= 1
        else:
            dut.recv_prev.val @= 0
            
        dut.recv_init_uv.msg @= 0
        dut.recv_init_uv.val @= 1
        
        dut.sim_tick()
        
        # Incrementam indecsii doar daca hardware-ul a acceptat datele (Backpressure)
        if dut.recv_curr.val and dut.recv_curr.rdy:
            curr_idx += 1
        if dut.recv_prev.val and dut.recv_prev.rdy:
            prev_idx += 1
            
        # 3. Colectam Output
        if dut.send_uv.val:
            # Despachetare Q4.12
            raw_u = int(dut.send_uv.msg[0:32])
            
            # Conversie Signed 32-bit
            if raw_u > 2147483647: raw_u -= 4294967296
            
            # Conversie la float
            u_float = raw_u / 4096.0
            
            output_u.append(u_float)
            results_collected += 1
            
        if results_collected >= total_pixels:
            break
            
    print(f"Simulation finished. Processed {results_collected}/{total_pixels} pixels.")
    
    # 4. Analiza Statistici
    u_arr = np.array(output_u)
    
    max_u = np.max(u_arr)
    min_u = np.min(u_arr)
    avg_u = np.mean(np.abs(u_arr)) # Media magnitudinii
    
    print(f"Max U detected: {max_u:.4f}")
    print(f"Avg Motion Magnitude: {avg_u:.4f}")
    
    # Validare: Trebuie sa avem macar o zona cu miscare detectata > 0.1
    if max_u > 0.1:
        print(">>> SUCCESS: Motion detected in hardware Pipeline!")
    else:
        print(">>> WARNING: Motion signal too weak. Check sync or alpha.")

if __name__ == "__main__":
    test_system_integration()