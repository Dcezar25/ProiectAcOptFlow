import sys
import os

# Calea catre root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass
from src.optical_flow_top import OpticalFlowTop

def translate():
    print("Starting Linux Translation")
    
    # Instantiere
    dut = OpticalFlowTop(img_width=64, alpha=10)
    
    # Configurare nume
    dut.set_metadata( VerilogTranslationPass.explicit_module_name, 'OpticalFlowTop' )
    
    # Traducere
    # Pe Linux, asta va genera OpticalFlowTop.v in folderul curent
    dut.apply( VerilogTranslationPass() )
    
    print("Done! Checking file...")
    if os.path.exists("OpticalFlowTop.v"):
        print(f"SUCCESS: {os.path.abspath('OpticalFlowTop.v')}")
    else:
        print("FAIL: File not found.")

if __name__ == "__main__":
    translate()