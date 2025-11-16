@echo off
echo ================================================
echo  Starting Price Tracker Application
echo ================================================
echo.

REM Start Flask Backend
echo [1/2] Starting Flask Backend on http://localhost:5000
start "Flask Backend" cmd /k "conda activate webdev && python app.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

REM Start React Frontend
echo [2/2] Starting React Frontend...
cd frontend
start "React Frontend" cmd /k "npm run dev"

echo.
echo ================================================
echo  Both servers are starting!
echo  - Backend: http://localhost:5000
echo  - Frontend: Check the terminal for the URL
echo ================================================
echo.
echo Press any key to exit this window...
pause > nul
