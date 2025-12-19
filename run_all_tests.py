import os
import subprocess

def ruleaza_testele():
    # Cream un folder pentru rezultate daca nu exista deja
    folder_rezultate = "rezultate_teste"
    if not os.path.exists(folder_rezultate):
        os.makedirs(folder_rezultate)

    # Lista cu toate testele din proiectul tau
    teste = [
        "tests/test_line_buffer.py",
        "tests/test_gradient.py",
        "tests/test_hs_core.py",
        "tests/test_pyramid_components.py",
        "tests/test_system.py",
        "tests/test_system_pyramid.py"
    ]

    print("Incepem verificarea componentelor")

    for cale_test in teste:
        # Generam numele fisierului txt pe baza numelui testului
        nume_test = os.path.basename(cale_test).replace(".py", ".txt")
        cale_output = os.path.join(folder_rezultate, nume_test)

        print("Se ruleaza " + cale_test)

        # Deschidem fisierul de log si rulam procesul
        with open(cale_output, "w") as log:
            # Folosim comanda python asa cum ai cerut
            rezultat = subprocess.run(["python", cale_test], stdout=log, stderr=subprocess.STDOUT, text=True)

            if rezultat.returncode == 0:
                print("Test trecut cu succes: " + nume_test)
            else:
                print("Problema detectata in " + nume_test + ". Detalii in folderul de rezultate")

    print("Procesul de testare s-a terminat")

if __name__ == "__main__":
    ruleaza_testele()