# Quick Fix: Database Connection Issue

## Problem
The FastAPI server shows database as "disconnected" even though MongoDB is running and has data.

## Solution
The database connection in the lifespan might be failing. Here's how to verify and fix:

### 1. Check MongoDB is Running
```bash
# Windows
net start MongoDB

# Or check if process is running
tasklist | findstr mongod
```

### 2. Verify Connection String
Check your `.env` file or environment variables:
```bash
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
```

### 3. Restart the Server
The server needs to be restarted to reconnect:

**Stop the server** (Ctrl+C in the terminal running uvicorn)

**Start it again:**
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Check Health Endpoint
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

### 5. Test API Endpoints
Once health shows "connected", test:
```bash
curl http://127.0.0.1:8000/projects/
curl http://127.0.0.1:8000/jobs/
```

## Alternative: Use New API Routes with Auth

The new routes at `/api/v1/*` might work better. They require authentication headers:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/projects?tenant_id=default" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: default"
```

## If Still Not Working

1. Check MongoDB logs for connection attempts
2. Verify firewall isn't blocking port 27017
3. Try connecting with mongosh: `mongosh mongodb://localhost:27017/`
4. Check if another application is using the port

