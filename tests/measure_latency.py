import sys
import os
from pymtl3 import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pyramidal_of_top import PyramidalOpticalFlow

def measure_latency():
    dut = PyramidalOpticalFlow( width=64 )
    dut.elaborate()
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    
    dut.send_uv.rdy @= 1
    
    start_cycle = -1
    end_cycle = -1
    
    print("Measuring Latency...")
    for cycle in range(5000):
        # Trimitem date constant
        dut.recv_curr.msg @= 100
        dut.recv_curr.val @= 1
        dut.recv_prev.msg @= 100
        dut.recv_prev.val @= 1
        
        # Notam cand incepe intrarea valida
        if cycle > 2 and start_cycle == -1:
            start_cycle = cycle
            
        dut.sim_tick()
        
        # Notam cand iese primul rezultat valid
        if dut.send_uv.val:
            end_cycle = cycle
            break
            
    if end_cycle != -1:
        latency = end_cycle - start_cycle
        print(f"========================================")
        print(f"LATENCY DETECTED: {latency} cycles")
        print(f"========================================")
    else:
        print("Simulation finished without output. Increase max cycles.")

if __name__ == "__main__":
    measure_latency()