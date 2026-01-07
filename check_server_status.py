"""Check server and database status"""
import requests
import sys
import time

print("=" * 60)
print("Checking Server Status")
print("=" * 60)

base_url = "http://127.0.0.1:8000"

# Check if server is responding
print("\n1. Checking if server is running...")
try:
    response = requests.get(f"{base_url}/", timeout=2)
    if response.status_code == 200:
        print("   [OK] Server is responding")
        data = response.json()
        print(f"   Message: {data.get('message')}")
    else:
        print(f"   [WARNING] Server returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   [ERROR] Server is not running or not accessible")
    print("   Please start the server: python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload")
    sys.exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    sys.exit(1)

# Check health
print("\n2. Checking database connection...")
try:
    response = requests.get(f"{base_url}/health", timeout=2)
    health = response.json()
    if health.get("status") == "healthy":
        print("   [OK] Database is connected")
    else:
        print(f"   [WARNING] Database status: {health.get('status')}")
        print(f"   Error: {health.get('error', 'Unknown')}")
        print("\n   Solution: Restart the server to reconnect to MongoDB")
except Exception as e:
    print(f"   [ERROR] Could not check health: {e}")

# Check projects
print("\n3. Testing projects endpoint...")
try:
    response = requests.get(f"{base_url}/projects/", timeout=5)
    if response.status_code == 200:
        projects = response.json()
        print(f"   [OK] Projects endpoint working")
        print(f"   Projects returned: {len(projects)}")
        if len(projects) > 0:
            print(f"   First project: {projects[0].get('name', 'N/A')}")
        else:
            print("   [WARNING] No projects returned (might be database connection issue)")
    else:
        print(f"   [ERROR] Projects endpoint returned status {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Could not fetch projects: {e}")

# Check jobs
print("\n4. Testing jobs endpoint...")
try:
    response = requests.get(f"{base_url}/jobs/", timeout=5)
    if response.status_code == 200:
        jobs = response.json()
        print(f"   [OK] Jobs endpoint working")
        print(f"   Jobs returned: {len(jobs)}")
        if len(jobs) > 0:
            print(f"   First job: {jobs[0].get('title', 'N/A')}")
        else:
            print("   [WARNING] No jobs returned (might be database connection issue)")
    else:
        print(f"   [ERROR] Jobs endpoint returned status {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Could not fetch jobs: {e}")

print("\n" + "=" * 60)
print("Status Check Complete")
print("=" * 60)
print("\nIf database shows as disconnected, restart the server:")
print("  1. Stop the server (Ctrl+C)")
print("  2. Run: python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload")

