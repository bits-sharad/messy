# How to Start FastAPI Server

## Quick Start

### Basic Command
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Step-by-Step Instructions

### Step 1: Navigate to Project Directory

Open terminal/command prompt and navigate to the project root:
```bash
cd F:\Mercer\mecy_api
```

### Step 2: Check if Server is Already Running

```bash
# Check if port 8000 is in use
netstat -ano | findstr ":8000" | findstr LISTENING
```

**If port 8000 is in use:**
- Find the terminal running the server and press `Ctrl+C` to stop it
- OR kill the process (see troubleshooting below)

### Step 3: Start the Server

Run this command:
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4: Watch for Success Messages

You should see:
```
============================================================
Starting FastAPI application...
============================================================
Attempting to connect to MongoDB...
  Connection string: mongodb://localhost:27017/
  Database name: job_matching_db
[OK] Connected to MongoDB database: job_matching_db
[OK] Database indexes created/verified
============================================================
FastAPI application ready!
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 5: Verify It's Running

**Check health:**
```bash
curl http://127.0.0.1:8000/health
```

**Or open in browser:**
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

---

## Command Options Explained

```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

- `python -m uvicorn` - Run uvicorn module
- `apps.main:app` - Import `app` from `apps/main.py`
- `--host 127.0.0.1` - Listen on localhost only (for security)
- `--port 8000` - Use port 8000
- `--reload` - Auto-reload on code changes (development mode)

---

## Alternative: Use Different Port

If port 8000 is busy:
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8001 --reload
```

Then access at: http://127.0.0.1:8001

---

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Troubleshooting

### Port Already in Use

**Find and kill process on port 8000:**

**Windows Command Prompt:**
```cmd
for /f "tokens=5" %a in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do taskkill /F /PID %a
```

**PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### Module Not Found Error

If you get `ModuleNotFoundError`:
```bash
# Install required packages
pip install fastapi uvicorn
```

### MongoDB Connection Issues

The server will start even if MongoDB is not connected, but data endpoints will return empty arrays.

**To connect MongoDB:**
1. Ensure MongoDB is running (see `MONGODB_START_GUIDE.md`)
2. Restart the server after MongoDB is running

---

## Running in Background (Optional)

### Windows (using start)

```cmd
start "FastAPI Server" cmd /k "python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload"
```

### Using Python script

Create `start_server.py`:
```python
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "uvicorn",
    "apps.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
])
```

Run:
```bash
python start_server.py
```

---

## Production Mode (Without Reload)

For production, remove `--reload` and use more workers:

```bash
uvicorn apps.main:app --host 0.0.0.0 --port 8000 --workers 4
```

⚠️ **Note:** `--reload` should only be used in development!

---

## Quick Reference

| Action | Command |
|--------|---------|
| **Start server** | `python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload` |
| **Stop server** | Press `Ctrl+C` |
| **Check if running** | `netstat -ano \| findstr ":8000"` |
| **Test health** | `curl http://127.0.0.1:8000/health` |
| **Access Swagger** | http://127.0.0.1:8000/docs |

---

## What Happens When Server Starts

1. ✅ Loads FastAPI application from `apps/main.py`
2. ✅ Connects to MongoDB (if available)
3. ✅ Creates/verifies database indexes
4. ✅ Registers all API routes
5. ✅ Starts listening on port 8000
6. ✅ Enables auto-reload on code changes

---

## After Starting

Once the server is running:

- ✅ **API endpoints**: http://127.0.0.1:8000
- ✅ **Swagger UI**: http://127.0.0.1:8000/docs
- ✅ **Health check**: http://127.0.0.1:8000/health
- ✅ **Projects**: http://127.0.0.1:8000/projects/
- ✅ **Jobs**: http://127.0.0.1:8000/jobs/

**The server will keep running until you stop it with `Ctrl+C`!** 🚀

