# Troubleshooting Guide

## Server Not Responding or Showing Errors

If you see "Failed to load jobs" or 500 errors:

### Solution 1: Restart the Server

The server needs to be restarted to pick up code changes. 

**Stop the current server** (if running):
- Press `Ctrl+C` in the terminal where the server is running

**Start the server again:**
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

### Solution 2: Check MongoDB Connection

If MongoDB is not running, the API will still work but return empty lists.

**To start MongoDB:**
- Windows: Start MongoDB service or run `mongod`
- Docker: `docker run -d -p 27017:27017 --name mongodb mongo`
- Or set `MONGODB_URL` environment variable to your MongoDB connection string

**To seed data after MongoDB is running:**
```bash
python run_seed_data.py
```

### Solution 3: Verify Server is Running

```bash
# Test root endpoint
curl http://127.0.0.1:8000/

# Test jobs endpoint
curl http://127.0.0.1:8000/jobs/

# Test projects endpoint
curl http://127.0.0.1:8000/projects/

# Check API docs
# Open browser: http://127.0.0.1:8000/docs
```

### Solution 4: Check Port Conflicts

If port 8000 is already in use:
```bash
# Use a different port
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8001 --reload

# Then update UI environment.ts to use port 8001
```

## UI Connection Issues

If UI shows "Failed to load" errors:

1. **Check backend is running:**
   - Visit http://127.0.0.1:8000/docs in browser
   - Should show Swagger UI

2. **Check CORS:**
   - CORS is configured to allow all origins
   - Should work out of the box

3. **Check API URL in UI:**
   - Verify `apps/ui/src/environments/environment.ts` has correct API URL
   - Should be: `http://127.0.0.1:8000`

4. **Check browser console:**
   - Press F12 → Console tab
   - Look for specific error messages

## Common Issues

### Issue: "Database not connected" warnings

**This is OK!** The API will still work but return empty lists until MongoDB is running and data is seeded.

### Issue: Empty lists in UI

**Normal behavior** if:
- MongoDB is not running
- No data has been seeded yet

**To fix:**
1. Start MongoDB
2. Run `python run_seed_data.py`
3. Refresh UI

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 8000 (Windows)
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8001 --reload
```

## Quick Health Check

Run these commands to verify everything:

```bash
# 1. Check server responds
curl http://127.0.0.1:8000/health

# 2. Check jobs endpoint (should return [] if no data)
curl http://127.0.0.1:8000/jobs/

# 3. Check projects endpoint (should return [] if no data)
curl http://127.0.0.1:8000/projects/

# 4. Check Swagger docs (open in browser)
# http://127.0.0.1:8000/docs
```

## Still Having Issues?

1. Check server logs in the terminal for specific error messages
2. Check browser console (F12) for client-side errors
3. Verify all dependencies are installed: `pip install -r requirements-rag.txt`
4. Make sure you're running from the project root directory

