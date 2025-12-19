import sys
import os
import io
import re
from pymtl3 import *

# Adaugam caile necesare
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pyramidal_of_top import PyramidalOpticalFlow

def test_demo_visualization():
    # --- CONFIGURARE PENTRU SCREENSHOT ---
    WIDTH = 32  # Folosim 32 biti ca sa nu mai avem erori de "too wide"
    
    print("Initializing Demo for Waveform Visualization...")
    dut = PyramidalOpticalFlow( width=WIDTH )
    dut.elaborate()
    
    # Activam Text Waveform
    dut.apply( DefaultPassGroup(textwave=True) )
    dut.sim_reset()
    
    print("Sending Dummy Data (10, 20, 30...)...")
    
    dut.send_uv.rdy @= 1
    
    # Regex pentru curatarea culorilor
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Trimitem 15 valori simple
    for i in range(15):
        val_curr = 10 * (i + 1)
        val_prev = val_curr + 5
        
        # 1. Trimitem date
        dut.recv_curr.msg @= val_curr
        dut.recv_curr.val @= 1
        
        dut.recv_prev.msg @= val_prev
        dut.recv_prev.val @= 1
        
        dut.sim_tick()

    # Mai rulam cateva cicluri fara date noi ca sa lasam pipeline-ul sa proceseze
    dut.recv_curr.val @= 0
    dut.recv_prev.val @= 0
    
    for _ in range(15):
        dut.sim_tick()

    print("Capturing Waveform...")
    
    # 2. Captura si Filtrare
    capture_buffer = io.StringIO()
    original_out = sys.stdout
    sys.stdout = capture_buffer
    dut.print_textwave()
    sys.stdout = original_out
    
    raw_content = capture_buffer.getvalue()
    clean_content = ansi_escape.sub('', raw_content) # Stergem culorile
    
    # 3. Pastram DOAR semnalele importante
    filtered_lines = []
    # Acestea sunt singurele semnale cerute in tema
    IMPORTANT_SIGS = ["recv_curr.msg", "recv_curr.val", "recv_prev.msg", "send_uv.msg", "send_uv.val"]
    
    lines = clean_content.split('\n')
    for line in lines:
        # Pastram header-ul (ciclurile)
        if len(line.strip()) > 0 and line.strip()[0].isdigit():
            filtered_lines.append(line)
            continue
            
        # Pastram doar liniile care contin numele semnalelor importante
        for kw in IMPORTANT_SIGS:
            if kw in line:
                filtered_lines.append(line)
                break
    
    # 4. Salvare
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
        
    with open("test_results/waveform_demo.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(filtered_lines))
        
    print("Done! Check 'test_results/waveform_demo.txt'")

if __name__ == "__main__":
    test_demo_visualization()