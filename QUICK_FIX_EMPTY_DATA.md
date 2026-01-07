# Quick Fix: Empty Jobs and Projects

## ✅ Solution: Restart the Server

The database has **9 jobs and 4 projects**, but the server isn't connected to MongoDB.

### Quick Fix Steps:

**Option 1: Use the batch file (Windows)**
```bash
restart_server_fix_data.bat
```

**Option 2: Manual restart**

1. **Stop the server:**
   - Press `Ctrl+C` in the terminal running the server

2. **Restart:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Wait for this message:**
   ```
   [OK] Connected to MongoDB database: job_matching_db
   ```

4. **Verify:**
   - Open: http://127.0.0.1:8000/docs
   - Try `GET /projects/` - should show 4 projects
   - Try `GET /jobs/` - should show 9 jobs

### Why This Happens

The server started before MongoDB was available. After restarting, it will connect during startup.

### After Restart

✅ Health: http://127.0.0.1:8000/health → `"database": "connected"`
✅ Projects: http://127.0.0.1:8000/projects/ → 4 projects
✅ Jobs: http://127.0.0.1:8000/jobs/ → 9 jobs
✅ UI: http://localhost:4200 → Shows data

**That's it!** Just restart the server and data will appear. 🎉


