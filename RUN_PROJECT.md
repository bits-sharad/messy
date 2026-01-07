# How to Run the Project

## Quick Start

The project consists of two services:
1. **FastAPI Backend** (Port 8000)
2. **Angular UI Frontend** (Port 4200)

## Running Both Services

### Option 1: Using Background Processes (Already Started)

Both services have been started in the background. You should be able to access:

- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Frontend UI**: http://localhost:4200 (may take 30-60 seconds to compile)

### Option 2: Manual Start

#### Start Backend (Terminal 1):
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Start Frontend (Terminal 2):
```bash
cd apps/ui
npm install  # First time only
npm start
```

## Verify Services Are Running

### Check Backend:
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"unhealthy","database":"disconnected",...}
```
*(Note: Database disconnected is OK - server still works, just won't have data)*

### Check Frontend:
Open browser: http://localhost:4200

### Check Ports:
```bash
# Windows
netstat -ano | findstr ":8000\|:4200" | findstr LISTENING

# Linux/Mac
lsof -i :8000 -i :4200
```

## Services Status

### ✅ FastAPI Backend
- **URL**: http://127.0.0.1:8000
- **Status**: Running
- **Documentation**: http://127.0.0.1:8000/docs
- **Database**: MongoDB (optional - server works without it)

### ✅ Angular UI
- **URL**: http://localhost:4200
- **Status**: Starting (compiling...)
- **Wait**: 30-60 seconds for first compilation

## Access Points

1. **Swagger UI (API Docs)**: http://127.0.0.1:8000/docs
2. **Frontend UI**: http://localhost:4200
3. **API Health**: http://127.0.0.1:8000/health
4. **Projects Endpoint**: http://127.0.0.1:8000/projects/
5. **Jobs Endpoint**: http://127.0.0.1:8000/jobs/

## Troubleshooting

### Backend Not Starting?
- Check if port 8000 is already in use
- Kill existing processes: `taskkill /F /FI "WINDOWTITLE eq *uvicorn*"`
- Try: `python -m uvicorn apps.main:app --host 127.0.0.1 --port 8001 --reload`

### Frontend Not Starting?
- Make sure you're in `apps/ui` directory
- Run `npm install` first
- Check if port 4200 is available
- Angular may take 1-2 minutes to compile on first start

### Database Connection Issues?
- MongoDB is optional - the server runs without it
- Endpoints will return empty arrays if DB is not connected
- To connect MongoDB: Install MongoDB and run it, or set `MONGODB_URL` env var

## Stopping Services

### Stop Backend:
- Press `Ctrl+C` in the terminal running uvicorn
- Or kill the process: `taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *uvicorn*"`

### Stop Frontend:
- Press `Ctrl+C` in the terminal running `npm start`

## Next Steps

1. **Open the UI**: http://localhost:4200
2. **Check API Docs**: http://127.0.0.1:8000/docs
3. **Test Endpoints**: Use Swagger UI to test API endpoints
4. **Add Data**: Use seed script: `python run_seed_data.py` (requires MongoDB)

## Features Available

- ✅ Projects CRUD operations
- ✅ Jobs CRUD operations  
- ✅ Semantic Job Search (RAG)
- ✅ Candidate-Job Matching (AI)
- ✅ Job Description Generation (GenAI)
- ✅ Question Answering (RAG)
- ✅ Mercer Job Library Integration


