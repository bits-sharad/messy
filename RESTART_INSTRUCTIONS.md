# Server Restart Instructions

## Problem
Multiple old server processes are stuck on port 8000, preventing the new server from starting.

## Solution

### Option 1: Use the Batch Script (Windows)
1. **Close all terminals running the server**
2. **Run this command:**
   ```bash
   restart_server.bat
   ```

### Option 2: Manual Restart

1. **Open Task Manager** (Ctrl+Shift+Esc)
2. **Find and end all Python processes:**
   - Look for processes named `python.exe` or `uvicorn`
   - End all of them

3. **Or use PowerShell:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

4. **Wait 2-3 seconds**

5. **Start the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Verify it works:**
   ```bash
   curl http://127.0.0.1:8000/projects/
   ```
   - Should return: `[]` (empty array, not "Internal Server Error")

### Option 3: Use Different Port (Quick Test)

If you can't kill the old processes:

1. **Update UI environment file:**
   - Edit: `apps/ui/src/environments/environment.ts`
   - Change: `apiUrl: 'http://127.0.0.1:8000'`
   - To: `apiUrl: 'http://127.0.0.1:8001'`

2. **Start server on port 8001:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8001 --reload
   ```

3. **Restart your UI**

## After Restart

Once the server is running with the new code:
- ✅ `/projects/` returns `[]` (not 500 error)
- ✅ `/jobs/` returns `[]` (not 500 error)
- ✅ UI loads without "Failed to load" errors
- ✅ Projects/Jobs pages show empty states (normal)

## Verify Fix

Test the endpoints:
```bash
# Should return [] (empty array)
curl http://127.0.0.1:8000/projects/
curl http://127.0.0.1:8000/jobs/

# Health check
curl http://127.0.0.1:8000/health
```

If you see `[]` instead of "Internal Server Error", the fix is working!

