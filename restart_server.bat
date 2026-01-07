@echo off
echo ============================================================
echo Restarting FastAPI Server
echo ============================================================
echo.

echo Stopping any existing server processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1

echo.
echo Waiting for ports to be released...
timeout /t 2 >nul

echo.
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo Server starting in new window...
echo.
echo Please wait 5-10 seconds for the server to fully start.
echo.
echo Then check:
echo   1. Health: curl http://127.0.0.1:8000/health
echo   2. Swagger: http://127.0.0.1:8000/docs
echo   3. Projects: curl http://127.0.0.1:8000/projects/
echo.
pause
