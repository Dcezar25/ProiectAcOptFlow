import sys
import os
import shutil
import time

# Setari cai
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass
from src.optical_flow_top import OpticalFlowTop

def find_and_rescue_verilog():
    print(f"Working Directory: {os.getcwd()}")
    print("Starting Translation")
    
    # 1. Instantiere si Elaborare
    dut = OpticalFlowTop(img_width=64, alpha=10)
    dut.set_metadata( VerilogTranslationPass.explicit_module_name, 'OpticalFlowTop' )
    
    print("Elaborating...")
    dut.elaborate()
    
    # 2. Aplicare Traducere
    print("Applying Verilog Translation Pass...")
    try:
        dut.apply( VerilogTranslationPass() )
    except Exception as e:
        print(f"[WARNING] Pass raised an exception (ignoring if file generated): {e}")

    # 3. CAUTARE RECURSIVA (Search and Rescue)
    print("Searching for generated file 'OpticalFlowTop.v'...")
    
    target_file = "OpticalFlowTop.v"
    found_path = None
    
    # Cautam in tot proiectul
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if target_file in files:
            found_path = os.path.join(root, target_file)
            break
            
    # 4. Rezultat
    if found_path:
        print(f"FOUND FILE AT: {found_path}")
        
        # Il mutam in root daca nu e deja acolo
        dest_path = os.path.join(PROJECT_ROOT, target_file)
        if os.path.abspath(found_path) != os.path.abspath(dest_path):
            print(f"Moving file to project root: {dest_path}")
            shutil.move(found_path, dest_path)
        else:
            print("File is already in the project root.")
            
        print("\n[SUCCESS] Verilog generation complete!")
        print(f"File ready at: {dest_path}")
    else:
        print("\n[FAIL] Could not find 'OpticalFlowTop.v' anywhere.")
        print("Listing all .v files found in project:")
        # Listam orice fisier .v gasit, poate are alt nume
        for root, dirs, files in os.walk(PROJECT_ROOT):
            for file in files:
                if file.endswith(".v"):
                    print(f" - {os.path.join(root, file)}")

if __name__ == "__main__":
    find_and_rescue_verilog()