"""Quick status check for backend and frontend"""
import requests
import time
import sys

print("=" * 60)
print("Project Status Check")
print("=" * 60)
print()

# Check Backend
print("Checking Backend (http://127.0.0.1:8000)...")
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=3)
    if response.status_code == 200:
        data = response.json()
        status = data.get("status", "unknown")
        db_status = data.get("database", "unknown")
        print(f"  Status: {status}")
        print(f"  Database: {db_status}")
        if status == "healthy":
            print("  [OK] Backend is running!")
        else:
            print("  [WARNING] Backend running but database not connected")
    else:
        print(f"  [ERROR] Backend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  [ERROR] Backend is not responding")
    print("  Please start the backend: python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload")
except Exception as e:
    print(f"  [ERROR] {e}")

print()

# Check Frontend
print("Checking Frontend (http://localhost:4200)...")
try:
    response = requests.get("http://localhost:4200", timeout=3)
    if response.status_code == 200:
        print("  [OK] Frontend is running!")
    else:
        print(f"  [WARNING] Frontend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  [WARNING] Frontend is not responding")
    print("  This is normal if it's still compiling (takes 30-60 seconds)")
    print("  Please check: cd apps/ui && npm start")
except Exception as e:
    print(f"  [WARNING] {e}")

print()
print("=" * 60)
print("Access Points:")
print("=" * 60)
print("  Backend API:       http://127.0.0.1:8000")
print("  Swagger UI:        http://127.0.0.1:8000/docs")
print("  Frontend UI:       http://localhost:4200")
print("  Health Check:      http://127.0.0.1:8000/health")
print("=" * 60)


