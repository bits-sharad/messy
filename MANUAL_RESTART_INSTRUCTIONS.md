# Manual Restart Instructions

## ✅ Quick Fix: Restart Server Manually

The server needs to be restarted manually to connect to MongoDB.

### Step 1: Stop the Server

**Find the terminal/command prompt where the server is running**, then:
- Press `Ctrl+C` to stop it

**OR kill all Python processes on port 8000:**

**Windows Command Prompt (cmd.exe):**
```cmd
for /f "tokens=5" %a in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do taskkill /F /PID %a
```

**PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### Step 2: Verify MongoDB is Running

```bash
# Check MongoDB
tasklist | findstr mongod
```

If not running, start it:
```bash
net start MongoDB
```

### Step 3: Start the Server

**In a new terminal/command prompt**, navigate to the project directory and run:

```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4: Watch for Success Messages

You should see:
```
Attempting to connect to MongoDB...
  Connection string: mongodb://localhost:27017/
  Database name: job_matching_db
[OK] Connected to MongoDB database: job_matching_db
[OK] Database indexes created/verified
============================================================
FastAPI application ready!
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 5: Verify It's Working

**Check health:**
```bash
curl http://127.0.0.1:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Check data:**
```bash
curl http://127.0.0.1:8000/projects/
curl http://127.0.0.1:8000/jobs/
```

Should return projects and jobs (not empty `[]`).

**Check in browser:**
- Swagger UI: http://127.0.0.1:8000/docs
- Frontend: http://localhost:4200

## Summary

1. ✅ Stop old server (Ctrl+C)
2. ✅ Verify MongoDB running
3. ✅ Start server: `python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload`
4. ✅ Look for `[OK] Connected to MongoDB`
5. ✅ Test endpoints

**After restart, you'll see:**
- 8 Projects
- 18 Jobs
- All data in Swagger UI and Angular UI

🎉 **That's it!**


