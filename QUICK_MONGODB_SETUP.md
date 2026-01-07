# Quick MongoDB URL Setup Guide

## 🎯 Where to Set MongoDB URL

The MongoDB URL is read from **environment variables** in `apps/database/connection.py`.

## ✅ Method 1: Create `.env` File (Easiest - Recommended)

### Step 1: Create `.env` file in project root

Create a file named `.env` in: `F:\Mercer\mecy_api\.env`

**Content:**
```env
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
```

### Step 2: Install python-dotenv (if not installed)

```bash
pip install python-dotenv
```

### Step 3: Restart Server

The `.env` file will be automatically loaded. Just restart your server:
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## ✅ Method 2: Set Windows Environment Variable

### PowerShell (Current Session):
```powershell
$env:MONGODB_URL="mongodb://localhost:27017/"
$env:MONGODB_DATABASE="job_matching_db"
```

### Command Prompt:
```cmd
set MONGODB_URL=mongodb://localhost:27017/
set MONGODB_DATABASE=job_matching_db
```

### Permanent (Windows):
1. Press `Win + R` → Type `sysdm.cpl` → Enter
2. Go to **Advanced** tab → Click **Environment Variables**
3. Under **User variables**, click **New**
4. Variable name: `MONGODB_URL`
5. Variable value: `mongodb://localhost:27017/`
6. Click **OK**
7. Repeat for `MONGODB_DATABASE` = `job_matching_db`
8. **Restart your terminal/server** for changes to take effect

---

## 📝 MongoDB URL Formats

### Local MongoDB (Default):
```
MONGODB_URL=mongodb://localhost:27017/
```

### With Authentication:
```
MONGODB_URL=mongodb://username:password@localhost:27017/
```

### MongoDB Atlas (Cloud):
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

### Remote MongoDB:
```
MONGODB_URL=mongodb://username:password@hostname:27017/
```

---

## 🔍 Verify It's Working

1. **Set the environment variable** (Method 1 or 2 above)

2. **Restart the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Check the logs** - You should see:
   ```
   Connected to MongoDB database: job_matching_db
   ```

4. **Test health endpoint:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   
   Should return:
   ```json
   {"status":"healthy","database":"connected"}
   ```

5. **Seed data** (optional):
   ```bash
   python run_seed_data.py
   ```

---

## 📍 File Location Reference

- **Code that reads MongoDB URL**: `apps/database/connection.py` (lines 15-19)
- **Environment variables used**:
  - `MONGODB_URL` (primary)
  - `MONGODB_URI` (alternative)
  - `MONGODB_DATABASE` (default: `job_matching_db`)

---

## 🐛 Troubleshooting

### Still seeing "Database not connected"?

1. **Check MongoDB is running:**
   ```bash
   # Windows - check service
   sc query MongoDB
   
   # Or start MongoDB
   net start MongoDB
   ```

2. **Verify environment variable:**
   ```bash
   # PowerShell
   echo $env:MONGODB_URL
   
   # Command Prompt
   echo %MONGODB_URL%
   ```

3. **Restart server after setting variables**

4. **Check connection string format** - Make sure it's correct

---

## 💡 Quick Example

**For local MongoDB:**

1. Create `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017/
   MONGODB_DATABASE=job_matching_db
   ```

2. Install dotenv:
   ```bash
   pip install python-dotenv
   ```

3. Restart server:
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

Done! 🎉


