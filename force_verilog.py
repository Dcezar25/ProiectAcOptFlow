import sys
import os

# Adaugam calea curenta
sys.path.append(os.getcwd())

from pymtl3 import *
# IMPORTANT: Folosim VerilogTranslationPass simplu, NU ImportPass
# ImportPass incearca sa compileze cu Verilator (care lipseste pe Windows)
# TranslationPass doar genereaza fisierul text.
from pymtl3.passes.backends.verilog import VerilogTranslationPass

from src.pyramidal_of_top import PyramidalOpticalFlow

def run_translation():
    print("========================================")
    print("   Starting Verilog Generation (No Compile)...")
    print("========================================")
    
    # 1. Instantiem modelul (64 biti latime)
    dut = PyramidalOpticalFlow( width=64 )
    
    # 2. Configuram Metadata
    # Ii spunem explicit sa activeze traducerea
    dut.set_metadata( VerilogTranslationPass.enable, True )
    
    # Putem forta un nume de fisier specific
    dut.set_metadata( VerilogTranslationPass.explicit_module_name, 'PyramidalOpticalFlow' )
    
    # 3. Elaborare
    print("Elaborating model...")
    dut.elaborate()
    
    # 4. Aplicam Pasul de Traducere Simpla
    print("Applying Verilog Translation Pass...")
    try:
        dut.apply( VerilogTranslationPass() )
        print("Translation Pass applied successfully.")
    except Exception as e:
        print(f"ERROR: {e}")

    # 5. Verificare
    expected_file = "PyramidalOpticalFlow.v"
    
    if os.path.exists(expected_file):
        print(f"\n>>> SUCCESS! Verilog file generated: {expected_file}")
        print("Deschide acest fisier cu Notepad/VS Code pentru a vedea codul hardware.")
    else:
        # Uneori PyMTL genereaza cu sufixe ciudate daca nu gaseste configuratia
        print("\n>>> Check folder for any .v file (e.g., PyramidalOpticalFlow__width_64.v)")
        files = [f for f in os.listdir('.') if f.endswith('.v')]
        if files:
            print(f"Found files: {files}")

if __name__ == "__main__":
    run_translation()