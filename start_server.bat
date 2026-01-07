@echo off
echo ============================================================
echo Starting FastAPI Server
echo ============================================================
echo.

echo Checking MongoDB connection...
python -c "from apps.database.connection import db_manager; db_manager.connect(); print('MongoDB: Connected' if db_manager.is_connected() else 'MongoDB: NOT Connected')"

echo.
echo Starting server...
echo.
echo Server will start at: http://127.0.0.1:8000
echo Swagger UI will be at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload

pause

