@echo off
echo ============================================================
echo Restarting FastAPI Server
echo ============================================================
echo.

echo Stopping existing server processes...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo.
echo Checking MongoDB connection...
python -c "from apps.database.connection import db_manager; db_manager.connect(); print('[OK] MongoDB Connected' if db_manager.is_connected() else '[ERROR] MongoDB NOT Connected'); db = db_manager.get_database(); print('[OK] Jobs in DB:', db.jobs.count_documents({})); print('[OK] Projects in DB:', db.projects.count_documents({}))"

echo.
echo ============================================================
echo Starting FastAPI Server...
echo ============================================================
echo.
echo Server will be available at:
echo   - API: http://127.0.0.1:8000
echo   - Swagger UI: http://127.0.0.1:8000/docs
echo   - Frontend: http://localhost:4200
echo.
echo Look for: [OK] Connected to MongoDB database
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload


