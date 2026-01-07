# Fix Database Connection Issue

## Current Status
MongoDB is running, but the FastAPI server shows "unhealthy" because the connection wasn't established at startup.

## Quick Fix Options

### Option 1: Restart Server (Recommended)

The server needs to be restarted so it can connect to MongoDB during startup.

**Steps:**

1. **Stop the server:**
   - Find the terminal where the server is running
   - Press `Ctrl+C` to stop it

2. **Restart the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Watch for these messages:**
   ```
   Attempting to connect to MongoDB...
     Connection string: mongodb://localhost:27017/
     Database name: job_matching_db
   [OK] Connected to MongoDB database: job_matching_db
   ```

4. **Verify it's working:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   
   Should return:
   ```json
   {"status": "healthy", "database": "connected"}
   ```

### Option 2: Health Check Will Auto-Reconnect

I've updated the health check endpoint to automatically reconnect if MongoDB is available. Just hit the health endpoint again:

```bash
curl http://127.0.0.1:8000/health
```

Or refresh: http://127.0.0.1:8000/health in your browser.

The health check will now attempt to reconnect automatically if the database is disconnected.

## Verify MongoDB is Running

✅ **MongoDB is confirmed running** on port 27017 (process ID: 12512)

To verify yourself:
```bash
netstat -ano | findstr ":27017" | findstr LISTENING
```

Or check MongoDB service:
```bash
sc query MongoDB
```

## Expected Behavior After Fix

Once connected, you should see:

1. **Health endpoint:**
   ```json
   {
     "status": "healthy",
     "database": "connected"
   }
   ```

2. **Projects endpoint returns data:**
   ```bash
   curl http://127.0.0.1:8000/projects/
   ```
   Should return projects (not empty `[]`)

3. **Jobs endpoint returns data:**
   ```bash
   curl http://127.0.0.1:8000/jobs/
   ```
   Should return jobs (not empty `[]`)

4. **Swagger UI shows data:**
   - Open: http://127.0.0.1:8000/docs
   - Try `GET /projects/` - should show projects
   - Try `GET /jobs/` - should show jobs

## If Still Not Working

1. **Check MongoDB service:**
   ```bash
   net start MongoDB
   ```

2. **Check environment variables:**
   ```bash
   # PowerShell
   echo $env:MONGODB_URL
   
   # Command Prompt
   echo %MONGODB_URL%
   ```

3. **Create `.env` file** (if not exists):
   ```
   MONGODB_URL=mongodb://localhost:27017/
   MONGODB_DATABASE=job_matching_db
   ```

4. **Test connection directly:**
   ```bash
   python -c "from apps.database.connection import db_manager; db_manager.connect(); print('Connected!' if db_manager.is_connected() else 'Failed')"
   ```

## Summary

- ✅ MongoDB is running
- ⚠️ Server needs to reconnect
- 🔄 Option 1: Restart server (best practice)
- 🔄 Option 2: Hit `/health` endpoint (auto-reconnect enabled)

After fixing, you should see "healthy" status and data in endpoints!


