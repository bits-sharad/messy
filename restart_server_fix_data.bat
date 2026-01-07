@echo off
echo ============================================================
echo Restarting Server to Fix Empty Data Issue
echo ============================================================
echo.

echo Step 1: Stopping existing server processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
timeout /t 2 >nul

echo Step 2: Checking MongoDB...
python -c "from apps.database.connection import db_manager; db_manager.connect(); print('MongoDB: Connected' if db_manager.is_connected() else 'MongoDB: NOT Connected'); db = db_manager.get_database(); print('Jobs in DB:', db.jobs.count_documents({})); print('Projects in DB:', db.projects.count_documents({}))"
echo.

echo Step 3: Starting server...
echo.
echo Server will start at: http://127.0.0.1:8000
echo Swagger UI: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:4200
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload

pause


