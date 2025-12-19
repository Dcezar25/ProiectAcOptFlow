import sys
import os
import subprocess
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"   RUNNING: {text}")
    print("="*60)

def run_test(script_path, description):
    print_header(description)
    
    start_time = time.time()
    
    # Verificam daca fisierul exista
    if not os.path.exists(script_path):
        print(f"❌ ERROR: Script not found: {script_path}")
        return False

    # Rulam scriptul ca un proces separat
    try:
        # capture_output=True ascunde output-ul daca vrei liniste, 
        # dar aici il lasam sa se vada ca sa stii ce se intampla.
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False, 
            text=True,
            check=False
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ PASS: {description} (Time: {duration:.2f}s)")
            return True
        else:
            print(f"\n❌ FAIL: {description} returned error code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return False

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   -> Found artifact: {filepath} ({size} bytes)")
        return True
    else:
        print(f"   -> MISSING artifact: {filepath}")
        return False

def main():
    print("🚀 STARTING FULL SYSTEM VERIFICATION 🚀")
    
    # Definim caile catre teste
    # Ajusteaza caile daca scripturile tale sunt in alte foldere
    test_math    = os.path.join("tests", "test_system_pyramid.py")
    test_wave    = os.path.join("tests", "test_demo_waveform.py")
    test_verilog = "force_verilog.py" # Sau scripts/force_verilog.py daca l-ai mutat
    
    results = []

    # 1. Rulare Simulare Matematica
    success_math = run_test(test_math, "Functional Simulation (Math & Logic)")
    results.append(("Simulation", success_math))

    # 2. Rulare Generare Waveforms
    success_wave = run_test(test_wave, "Waveform Generation")
    results.append(("Waveforms", success_wave))
    
    # Verificam daca a creat fisierul waveform
    if success_wave:
        check_file_exists("test_results/waveform_demo.txt", "Waveform Output")

    # 3. Rulare Traducere Verilog
    success_verilog = run_test(test_verilog, "Hardware Synthesis (Verilog Translation)")
    results.append(("Verilog", success_verilog))
    
    # Verificam daca a creat fisierul .v
    if success_verilog:
        check_file_exists("PyramidalOpticalFlow.v", "Verilog Source")

    # --- RAPORT FINAL ---
    print("\n" + "#"*60)
    print("📊  FINAL REPORT SUMMARY")
    print("#"*60)
    
    all_passed = True
    for name, status in results:
        icon = "✅ PASS" if status else "❌ FAIL"
        print(f"{name:<20} : {icon}")
        if not status: all_passed = False
        
    print("-" * 60)
    if all_passed:
        print("🏆  CONGRATULATIONS! The project is fully verified and ready.")
    else:
        print("⚠️  WARNING: Some tests failed. Check log above.")
    print("#"*60)

if __name__ == "__main__":
    main()