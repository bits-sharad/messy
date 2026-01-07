"""Script to index all jobs for semantic search"""
import requests
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager
from apps.services.mmc_jobs import JobService
from apps.core.client import CoreAPIClient


async def index_all_jobs():
    """Index all jobs for semantic search"""
    print("=" * 60)
    print("Indexing All Jobs for Semantic Search")
    print("=" * 60)
    
    # Connect to database
    db_manager.connect()
    if not db_manager.is_connected():
        print("[ERROR] Could not connect to database")
        return
    
    print("[OK] Connected to database")
    
    # Get all jobs
    core_api = CoreAPIClient()
    job_service = JobService(core_api)
    
    print("\nFetching all jobs...")
    result = await job_service.list_all_jobs(tenant_id="default", skip=0, limit=1000)
    jobs = result.get("jobs", [])
    
    if not jobs:
        print("[WARNING] No jobs found in database")
        print("Please seed data first: python run_seed_data.py")
        return
    
    print(f"[OK] Found {len(jobs)} jobs to index\n")
    
    # Index each job
    base_url = "http://127.0.0.1:8000/api/v1/ai/jobs"
    headers = {
        "X-Principal-Subject": "system",
        "X-Tenant-ID": "default"
    }
    
    indexed = 0
    failed = 0
    
    for i, job in enumerate(jobs, 1):
        job_id = job.get("id")
        job_title = job.get("title", "Unknown")
        
        try:
            response = requests.post(
                f"{base_url}/{job_id}/index",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                indexed += 1
                print(f"[{i}/{len(jobs)}] [OK] Indexed: {job_title}")
            else:
                failed += 1
                print(f"[{i}/{len(jobs)}] [FAILED] {job_title}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            failed += 1
            print(f"[{i}/{len(jobs)}] [ERROR] {job_title}: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    print("Indexing Complete")
    print("=" * 60)
    print(f"Total jobs: {len(jobs)}")
    print(f"Successfully indexed: {indexed}")
    print(f"Failed: {failed}")
    print("\nYou can now use semantic search!")


if __name__ == "__main__":
    try:
        asyncio.run(index_all_jobs())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Indexing cancelled")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

