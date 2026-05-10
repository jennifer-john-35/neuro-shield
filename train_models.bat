@echo off
echo.
echo  ========================================
echo   NEURO-SHIELD — Train AI Models
echo  ========================================
echo.
cd /d "%~dp0"
call venv\Scripts\activate

echo  [1/2] Generating 10,000 IMU training samples...
python ml\generate_imu_data.py

echo.
echo  [2/2] Training LSTM crash classifier + Grey-Spot predictor...
python ml\train_lstm.py
python ml\greyspot_predictor.py

echo.
echo  All models saved in ml\models\
pause
