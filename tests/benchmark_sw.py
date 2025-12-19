import time
import numpy as np

def software_optical_flow_dummy(size=64):
    # Simulare procesare: parcurgere pixeli + calcule matematice simple
    # Asta simuleaza complexitatea Lucas-Kanade pe CPU
    img = np.random.randint(0, 255, (size, size))
    res = np.zeros((size, size))
    
    start = time.time()
    # Iteram pixel cu pixel (cum face un CPU clasic, nu vectorizat)
    for y in range(1, size-1):
        for x in range(1, size-1):
            # Calcule fictive similare cu LK (gradiente + inmultiri)
            grad_x = int(img[y, x+1]) - int(img[y, x-1])
            grad_y = int(img[y+1, x]) - int(img[y-1, x])
            val = (grad_x * grad_y) / 10.0
            res[y, x] = val
    end = time.time()
    return end - start

def calculate_hardware_time(cycles, frequency_mhz=100, num_pixels=4096):
    # Timpul HW = (Nr Pixeli + Latenta) * Perioada Ceasului
    # La 100 MHz, perioada = 10ns
    # Pipeline-ul proceseaza 1 pixel/ciclu dupa ce trece latenta
    total_cycles = num_pixels + cycles # (latency from Step 2)
    time_sec = total_cycles * (1 / (frequency_mhz * 1e6))
    return time_sec

if __name__ == "__main__":
    # 1. Masoara Software
    sw_time = software_optical_flow_dummy(64)
    print(f"Software Time (CPU): {sw_time:.6f} seconds")
    
    # 2. Calculeaza Hardware (Pune latenta obtinuta la pasul 2, ex: 300)
    LATENCY = 300 
    hw_time = calculate_hardware_time(LATENCY, frequency_mhz=100)
    print(f"Hardware Time (FPGA 100MHz): {hw_time:.6f} seconds")
    
    # 3. Speedup
    print(f"Speedup: {sw_time / hw_time:.2f}x faster on FPGA")
    print(f"Speedup: {sw_time / hw_time:.2f}x faster on FPGA")