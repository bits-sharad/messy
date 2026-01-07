# Fix: No Jobs/Projects Showing

## Problem
The database has data (9 jobs, 4 projects), but the API endpoints return empty arrays `[]`.

## Root Cause
The FastAPI server started before MongoDB was available, so the database connection wasn't established. Even though MongoDB is now running and has data, the server's `db_manager` instance hasn't reconnected.

## Solution: Restart the Server

**The server needs to be restarted to establish the MongoDB connection.**

### Steps:

1. **Stop the server:**
   - Find the terminal/process running: `python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload`
   - Press `Ctrl+C` to stop it

2. **Verify MongoDB is running:**
   ```bash
   # Check MongoDB process
   tasklist | findstr mongod
   
   # Or check port
   netstat -ano | findstr ":27017" | findstr LISTENING
   ```

3. **Restart the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. **Watch for these messages:**
   ```
   Attempting to connect to MongoDB...
     Connection string: mongodb://localhost:27017/
     Database name: job_matching_db
   [OK] Connected to MongoDB database: job_matching_db
   [OK] Database indexes created/verified
   ```

5. **Verify it's working:**
   ```bash
   # Check health
   curl http://127.0.0.1:8000/health
   ```
   Should show: `"database": "connected"`

   ```bash
   # Check data
   curl http://127.0.0.1:8000/projects/
   ```
   Should return 4 projects (not empty `[]`)

   ```bash
   # Check jobs
   curl http://127.0.0.1:8000/jobs/
   ```
   Should return 9 jobs (not empty `[]`)

## Alternative: Verify Data is in Database

If you want to confirm data exists before restarting:

```bash
python -c "from apps.database.connection import db_manager; db_manager.connect(); db = db_manager.get_database(); print('Jobs:', db.jobs.count_documents({})); print('Projects:', db.projects.count_documents({}))"
```

Should show:
```
Jobs: 9
Projects: 4
```

## After Restart

Once the server restarts and connects:

✅ **Health endpoint** will show: `"database": "connected"`
✅ **Projects endpoint** will return 4 projects
✅ **Jobs endpoint** will return 9 jobs
✅ **Swagger UI** will show data (not empty arrays)
✅ **Angular UI** will display projects and jobs

## Quick Test Script

Run this to verify everything is working:

```bash
python check_project_status.py
```

Then test endpoints:

```bash
# Test projects
curl http://127.0.0.1:8000/projects/ | python -m json.tool

# Test jobs
curl http://127.0.0.1:8000/jobs/ | python -m json.tool
```

## Summary

- ✅ **Database has data**: 9 jobs, 4 projects
- ⚠️ **Server not connected**: Needs restart
- 🔄 **Fix**: Restart the FastAPI server

After restart, all endpoints will work correctly!


