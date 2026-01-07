"""Test API endpoints to see what's being returned"""
import requests
import json

base_url = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing API Endpoints")
print("=" * 60)

# Test old routes (no auth required)
print("\n1. Testing OLD routes (no auth):")
print("-" * 60)

try:
    response = requests.get(f"{base_url}/projects/")
    print(f"GET /projects/ - Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First project: {json.dumps(data[0], indent=2, default=str)[:200]}")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

try:
    response = requests.get(f"{base_url}/jobs/")
    print(f"\nGET /jobs/ - Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First job: {json.dumps(data[0], indent=2, default=str)[:200]}")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

# Test new routes (auth required)
print("\n\n2. Testing NEW routes (with auth):")
print("-" * 60)

headers = {
    "X-Principal-Subject": "test-user",
    "X-Tenant-ID": "default"
}

try:
    response = requests.get(f"{base_url}/api/v1/projects", params={"tenant_id": "default"}, headers=headers)
    print(f"GET /api/v1/projects - Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First project: {json.dumps(data[0], indent=2, default=str)[:200]}")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

try:
    response = requests.get(f"{base_url}/api/v1/projects/695e3221efa74c826ffa04ef/jobs", headers=headers)
    print(f"\nGET /api/v1/projects/{{id}}/jobs - Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First job: {json.dumps(data[0], indent=2, default=str)[:200]}")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)

