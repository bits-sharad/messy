# Server Status & Troubleshooting

## Current Status
Server restarted. Please check the server terminal window for startup messages.

## Verify Server is Running

### 1. Check Health
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Test Endpoints

**Projects:**
```bash
curl http://127.0.0.1:8000/projects/
```
Should return 4 projects.

**Jobs:**
```bash
curl http://127.0.0.1:8000/jobs/
```
Should return 9 jobs.

### 3. Check Swagger UI
Open: http://127.0.0.1:8000/docs

Try the endpoints - they should show data, not empty arrays.

## If Database Still Shows as Disconnected

The server terminal should show connection messages. Look for:

**✅ Good signs:**
```
[OK] Connected to MongoDB database: job_matching_db
[OK] Database indexes created/verified
```

**❌ Problems:**
```
[ERROR] Failed to connect to MongoDB
```

### Quick Fixes:

1. **Ensure MongoDB is running:**
   ```bash
   # Check if MongoDB is running
   tasklist | findstr mongod
   
   # If not, start it:
   net start MongoDB
   ```

2. **Restart server manually:**
   - Stop server (Ctrl+C)
   - Run: `python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload`
   - Watch for connection messages

3. **Use the batch file:**
   ```bash
   start_server.bat
   ```
   This will check MongoDB connection first, then start the server.

## Expected Behavior

After successful restart:
- ✅ Health endpoint shows "healthy"
- ✅ `/projects/` returns 4 projects
- ✅ `/jobs/` returns 9 jobs
- ✅ Swagger UI shows data (not empty arrays)
- ✅ Angular UI displays projects and jobs

---

**Check your server terminal window** - it will show the connection status and any errors!

