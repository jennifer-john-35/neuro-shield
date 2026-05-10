@echo off
echo.
echo  ========================================
echo   NEURO-SHIELD v2.0 — Pure Python
echo  ========================================
echo.
cd /d "%~dp0"

if not exist venv (
    echo  [1/3] Creating virtual environment...
    python -m venv venv
)

echo  [2/3] Installing dependencies...
call venv\Scripts\activate
pip install flask "qrcode[pil]" Pillow numpy scikit-learn joblib requests python-dotenv --quiet

echo  [3/3] Starting NEURO-SHIELD...
echo.
echo  Dashboard  → http://localhost:8000
echo  Hospital   → http://localhost:8000/hospital
echo  Grey-Spot  → http://localhost:8000/greyspot
echo  Sentinel   → http://localhost:8000/sentinel
echo  Medical ID → http://localhost:8000/medical
echo  API Health → http://localhost:8000/api/health
echo.
echo  Press Ctrl+C to stop.
echo.
python app\main.py
