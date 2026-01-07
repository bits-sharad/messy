"""Test route with direct database access"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager
from apps.models.project import Project
from apps.models.job import Job

async def test():
    print("=" * 60)
    print("Testing Direct Database Access")
    print("=" * 60)
    
    # Connect
    print("\n1. Connecting to database...")
    db_manager.connect()
    
    if not db_manager.is_connected():
        print("[ERROR] Could not connect to database")
        return
    
    print("[OK] Connected")
    
    # Get database
    try:
        db = db_manager.get_database()
        
        # Query projects directly
        print("\n2. Querying projects directly...")
        projects_collection = Project.get_collection(db)
        projects = list(projects_collection.find({}).limit(5))
        print(f"   Found {len(projects)} projects")
        
        if projects:
            for p in projects:
                print(f"   - {p.get('name')} (ID: {str(p.get('_id'))})")
        
        # Query jobs directly
        print("\n3. Querying jobs directly...")
        jobs_collection = Job.get_collection(db)
        jobs = list(jobs_collection.find({}).limit(5))
        print(f"   Found {len(jobs)} jobs")
        
        if jobs:
            for j in jobs:
                print(f"   - {j.get('title')} (ID: {str(j.get('_id'))})")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test())

