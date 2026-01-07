# MongoDB URL Configuration Guide

## Where to Set MongoDB URL

The MongoDB URL is configured via **environment variables**. The application looks for these in order:

1. `MONGODB_URL` (primary)
2. `MONGODB_URI` (alternative)
3. Default: `mongodb://localhost:27017/` (if neither is set)

## Method 1: Create `.env` File (Recommended)

Create a `.env` file in the **project root** (`F:\Mercer\mecy_api\.env`):

```bash
# Local MongoDB
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db

# Or MongoDB Atlas (Cloud)
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name

# Or Remote MongoDB
# MONGODB_URL=mongodb://username:password@host:27017/database_name
```

**Note**: You may need to install `python-dotenv` to load `.env` files:
```bash
pip install python-dotenv
```

Then update `apps/main.py` or `apps/database/connection.py` to load the `.env` file:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Method 2: Set Environment Variable (Windows)

### PowerShell:
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
1. Open **System Properties** → **Environment Variables**
2. Add `MONGODB_URL` = `mongodb://localhost:27017/`
3. Add `MONGODB_DATABASE` = `job_matching_db`

## Method 3: Set Environment Variable (Linux/Mac)

```bash
export MONGODB_URL="mongodb://localhost:27017/"
export MONGODB_DATABASE="job_matching_db"
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export MONGODB_URL="mongodb://localhost:27017/"' >> ~/.bashrc
echo 'export MONGODB_DATABASE="job_matching_db"' >> ~/.bashrc
source ~/.bashrc
```

## MongoDB Connection String Formats

### Local MongoDB (Default):
```
mongodb://localhost:27017/
```

### With Authentication:
```
mongodb://username:password@localhost:27017/database_name
```

### MongoDB Atlas (Cloud):
```
mongodb+srv://username:password@cluster-name.mongodb.net/database_name?retryWrites=true&w=majority
```

### Remote MongoDB:
```
mongodb://username:password@hostname:27017/database_name
```

## Database Name Configuration

Set the database name with:
- `MONGODB_DATABASE` environment variable
- Default: `job_matching_db`

## Verification

After setting the MongoDB URL:

1. **Restart the FastAPI server**:
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Check health endpoint**:
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   
   Should return:
   ```json
   {"status":"healthy","database":"connected"}
   ```

3. **Check connection in logs**:
   Look for: `"Connected to MongoDB database: job_matching_db"`

## Install MongoDB (If Not Installed)

### Windows:
1. Download from: https://www.mongodb.com/try/download/community
2. Install MongoDB Community Server
3. Start MongoDB service:
   ```cmd
   net start MongoDB
   ```

### macOS (Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get install mongodb
sudo systemctl start mongod
sudo systemctl enable mongod
```

## Seed Data After Connection

Once MongoDB is connected, seed the database with dummy data:

```bash
python run_seed_data.py
```

This will create:
- Sample projects
- Sample jobs
- Ready-to-test data

## Troubleshooting

### "Failed to connect to MongoDB"
- **Check MongoDB is running**: `mongosh` or `mongo` command
- **Check port**: Default is `27017`
- **Check firewall**: Ensure port 27017 is not blocked
- **Check connection string**: Verify URL format is correct

### "Database not connected"
- Restart the FastAPI server after setting environment variables
- Check environment variables are set correctly
- Verify MongoDB service is running

### Connection Timeout
- Increase timeout in `apps/database/connection.py`:
  ```python
  serverSelectionTimeoutMS=10000  # 10 seconds
  ```

## Current Configuration Location

The MongoDB URL is read from:
- **File**: `apps/database/connection.py`
- **Lines**: 15-19
- **Code**:
  ```python
  self.connection_string = os.getenv(
      "MONGODB_URL", 
      os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
  )
  self.database_name = os.getenv("MONGODB_DATABASE", "job_matching_db")
  ```

## Quick Start Example

1. **Create `.env` file**:
   ```bash
   MONGODB_URL=mongodb://localhost:27017/
   MONGODB_DATABASE=job_matching_db
   ```

2. **Install python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

3. **Update connection.py** to load `.env`:
   Add at the top:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. **Restart server**:
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Verify**:
   ```bash
   curl http://127.0.0.1:8000/health
   ```


