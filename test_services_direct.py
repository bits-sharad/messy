"""Test services directly to see what's happening"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager
from apps.services.project_service import ProjectService
from apps.services.job_service import JobService

async def test_services():
    print("=" * 60)
    print("Testing Services Directly")
    print("=" * 60)
    
    # Connect to database
    db_manager.connect()
    
    if not db_manager.is_connected():
        print("[ERROR] Database not connected")
        return
    
    print("\n1. Testing ProjectService.list_projects()...")
    try:
        result = await ProjectService.list_projects(
            tenant_id="default",
            skip=0,
            limit=10
        )
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result) if isinstance(result, list) else 'N/A'}")
        if isinstance(result, list) and len(result) > 0:
            print(f"   First project ID: {result[0].id}")
            print(f"   First project name: {result[0].name}")
        else:
            print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. Testing JobService.list_jobs()...")
    try:
        result = await JobService.list_jobs(
            project_id=None,
            skip=0,
            limit=10
        )
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result) if isinstance(result, list) else 'N/A'}")
        if isinstance(result, list) and len(result) > 0:
            print(f"   First job ID: {result[0].id}")
            print(f"   First job title: {result[0].title}")
        else:
            print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_services())

