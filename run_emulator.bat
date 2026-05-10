@echo off
echo.
echo  ========================================
echo   NEURO-SHIELD — Sentinel Node Emulator
echo  ========================================
echo.
cd /d "%~dp0"
call venv\Scripts\activate
python ml\edge_emulator.py --mode interactive
