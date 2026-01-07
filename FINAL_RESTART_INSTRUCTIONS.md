# Final Restart Instructions

## ⚠️ Important: Manual Restart Required

The server is running but the database connection may not have initialized properly during startup. 

## Steps to Fix

### 1. Stop All Server Processes

Open the terminal where the server is running and press **`Ctrl+C`** to stop it.

OR kill all Python processes (if needed):
```bash
taskkill /F /IM python.exe
```

### 2. Verify MongoDB is Running

```bash
tasklist | findstr mongod
```

If MongoDB is not running, start it:
```bash
net start MongoDB
```

### 3. Restart Server

Run this command in your terminal:
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

**Watch for these messages in the terminal:**
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
```

### 4. Verify It's Working

**Check Health:**
```bash
curl http://127.0.0.1:8000/health
```
Should show: `"status": "healthy"`

**Check Swagger:**
1. Open: http://127.0.0.1:8000/docs
2. Try `GET /projects/` - should show 4 projects (not `[]`)
3. Try `GET /jobs/` - should show 9 jobs (not `[]`)

## What to Look For

✅ **Success indicators:**
- Terminal shows `[OK] Connected to MongoDB database`
- Health endpoint returns `"status": "healthy"`
- `/projects/` returns 4 projects
- `/jobs/` returns 9 jobs
- Swagger shows data (not empty arrays)

❌ **If still not working:**
- Check server terminal for error messages
- Verify MongoDB is actually running: `mongosh mongodb://localhost:27017/`
- Check if port 8000 is free: `netstat -an | findstr "8000"`

## Quick Test Script

After restarting, run:
```bash
python check_server_status.py
```

This will check all endpoints and show what's working.

---

**The server must be restarted manually in a terminal window** for you to see the connection messages and verify it's working properly.

