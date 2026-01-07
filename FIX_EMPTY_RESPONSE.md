# Fix: Empty Response in Swagger

## Problem
Swagger shows `[]` (empty array) for `/projects/` and `/jobs/` endpoints even though data exists in MongoDB.

## Root Cause
The FastAPI server's database connection isn't being established properly when routes are called, causing `db_manager.is_connected()` to return `False`, which makes services return empty arrays.

## Solution Applied

I've updated the services to **automatically reconnect** if the database connection is lost:

1. **`apps/services/project_service.py`** - Now attempts to reconnect before querying
2. **`apps/services/job_service.py`** - Now attempts to reconnect before querying

## What to Do

### Option 1: Wait for Auto-Reload (Fastest)
The server is running with `--reload`, so it should automatically detect the file changes and restart. Wait 5-10 seconds and try Swagger again.

### Option 2: Manual Restart (If auto-reload doesn't work)

1. **Stop the server** (Ctrl+C in the terminal running uvicorn)

2. **Restart it:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Watch for connection messages:**
   ```
   [OK] Connected to MongoDB database: job_matching_db
   ```

## Verify It's Working

After restart/waiting:

1. **Check health:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   Should show: `"status": "healthy"`

2. **Test in Swagger:**
   - Open: http://127.0.0.1:8000/docs
   - Try `GET /projects/` - should show 4 projects
   - Try `GET /jobs/` - should show 9 jobs

3. **Test via curl:**
   ```bash
   curl http://127.0.0.1:8000/projects/
   curl http://127.0.0.1:8000/jobs/
   ```

## What Changed

The services now:
- Check if database is connected
- **Automatically reconnect** if not connected
- Handle connection errors gracefully
- Still return data even if connection was initially lost

This ensures data will be returned even if the server started before MongoDB was fully ready.

