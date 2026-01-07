# MongoDB Start Guide - Access Denied Fix

## Problem
You got "Access is denied" when trying to start MongoDB. This means you need administrator privileges.

## Solution Options

### Option 1: Check if MongoDB is Already Running (Most Likely)

**MongoDB might already be running!** Let's check:

```bash
# Check if MongoDB process exists
tasklist | findstr mongod

# Check if port 27017 is in use
netstat -ano | findstr ":27017" | findstr LISTENING
```

**If MongoDB is running**, you'll see:
- A `mongod.exe` process in tasklist
- Port 27017 showing as LISTENING

**If it's running, you're good!** Just restart the FastAPI server.

### Option 2: Start MongoDB as Administrator

**Windows:**
1. **Right-click** on Command Prompt or PowerShell
2. Select **"Run as administrator"**
3. Then run:
   ```bash
   net start MongoDB
   ```

**OR use PowerShell (as admin):**
```powershell
Start-Service MongoDB
```

### Option 3: Check MongoDB Service Status

```bash
sc query MongoDB
```

This will show:
- `STATE: 1 STOPPED` - MongoDB is not running
- `STATE: 4 RUNNING` - MongoDB is already running ✅

### Option 4: Start MongoDB Manually (If Service Not Configured)

If MongoDB is installed but not as a service, you can start it manually:

1. **Find MongoDB installation path** (usually):
   - `C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe`
   - Or `C:\mongodb\bin\mongod.exe`

2. **Create data directory** (if doesn't exist):
   ```bash
   mkdir C:\data\db
   ```

3. **Start MongoDB manually:**
   ```bash
   "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db
   ```

   *(Replace version number with your MongoDB version)*

### Option 5: Use Docker (If Installed)

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Quick Test

**Test if MongoDB is accessible:**

```bash
python -c "from apps.database.connection import db_manager; db_manager.connect(); print('✅ Connected!' if db_manager.is_connected() else '❌ Not Connected')"
```

## Most Common Situation

**MongoDB is usually already running!** 

The "Access is denied" error just means you don't have admin rights to START it, but it might already be running.

**Check first:**
```bash
# This will show if MongoDB is running
tasklist | findstr mongod
netstat -ano | findstr ":27017"
```

**If MongoDB is running, you just need to restart the FastAPI server:**
```bash
# Stop server (Ctrl+C in server terminal)
# Then start again:
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

## Summary

1. ✅ **Check if MongoDB is already running** (most likely!)
2. ✅ If running → Just restart FastAPI server
3. ✅ If not running → Start MongoDB as administrator
4. ✅ Test connection with Python script above

**The server restart will work once MongoDB is accessible!** 🚀

