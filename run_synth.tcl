# 1. Definirea Part-ului (Cipul FPGA)
# Folosim un cip comun (Artix-7), des intalnit in laboratoare (Basys 3)
set_part xc7a35tcpg236-1

# 2. Citirea Fisierului Verilog generat de tine
# Asigura-te ca numele fisierului este corect!
read_verilog PyramidalOpticalFlow.v

# 3. Rularea Sintezei
# "top" trebuie sa fie numele Modulului din fisierul Verilog (PyramidalOpticalFlow)
synth_design -top PyramidalOpticalFlow -part xc7a35tcpg236-1

# 4. Generarea Rapoartelor (Aici sunt datele de aur!)
# Raport Utilizare (LUTs, Registers, DSP)
report_utilization -file report_utilization.txt

# Raport Putere (Consum in Watts)
report_power -file report_power.txt

# Raport Timing (Frecventa maxima teoretica)
report_timing_summary -file report_timing.txt

puts "======================================================="
puts "   SUCCESS: Rapoarte generate (utilization, power)!"
puts "======================================================="
exit