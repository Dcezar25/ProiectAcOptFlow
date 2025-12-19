@echo off
echo ==========================================
echo   Initializare Proiect Optical Flow PyMTL
echo ==========================================

:: 1. Creare Foldere Principale
if not exist "docs" mkdir docs
if not exist "src" mkdir src
if not exist "tests" mkdir tests
if not exist "golden_model" mkdir golden_model
if not exist "scripts" mkdir scripts
if not exist "build" mkdir build

:: 2. Creare README
echo # Optical Flow FPGA Implementation > README.md
echo. >> README.md
echo ## Project Structure >> README.md
echo - **src/**: PyMTL3 hardware source code >> README.md
echo - **golden_model/**: Python reference implementation (Horn-Schunck) >> README.md
echo - **tests/**: Verification scripts >> README.md
echo. >> README.md
echo ## How to run >> README.md
echo 1. Install requirements: `pip install -r requirements.txt` >> README.md

:: 3. Creare .gitignore (Esential pentru Git)
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo build/ >> .gitignore
echo .pytest_cache/ >> .gitignore
echo *.vcd >> .gitignore
echo .vscode/ >> .gitignore

:: 4. Creare requirements.txt
echo pymtl3 >= 3.1 > requirements.txt
echo numpy >> requirements.txt
echo opencv-python >> requirements.txt
echo matplotlib >> requirements.txt
echo pytest >> requirements.txt

:: 5. Creare fisier gol pentru module PyMTL
echo # Init file > src\__init__.py

echo.
echo [SUCCESS] Structura a fost creata!
echo Urmatorul pas: Deschide terminalul si ruleaza 'pip install -r requirements.txt'
pause