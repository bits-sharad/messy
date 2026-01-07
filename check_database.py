"""Quick script to check database contents"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager

# Connect to database
db_manager.connect()

if db_manager.is_connected():
    db = db_manager.get_database()
    
    # Check collections
    collections = db.list_collection_names()
    print("=" * 60)
    print("MongoDB Collections:")
    print("=" * 60)
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  {coll}: {count} documents")
    
    # Show sample projects
    print("\n" + "=" * 60)
    print("Sample Projects:")
    print("=" * 60)
    projects = list(db.projects.find().limit(5))
    for p in projects:
        print(f"  - {p.get('name')} (ID: {p.get('_id')})")
        print(f"    Status: {p.get('status')}, Tenant: {p.get('tenant_id')}")
    
    # Show sample jobs
    print("\n" + "=" * 60)
    print("Sample Jobs:")
    print("=" * 60)
    jobs = list(db.jobs.find().limit(5))
    for j in jobs:
        print(f"  - {j.get('title')} (Code: {j.get('job_code')})")
        print(f"    Status: {j.get('status')}, Project: {j.get('project_id')}")
    
    # Check job_documents if it exists
    if "job_documents" in collections:
        doc_count = db.job_documents.count_documents({})
        processed_count = db.job_documents.count_documents({"processed": True})
        print("\n" + "=" * 60)
        print("Job Documents:")
        print("=" * 60)
        print(f"  Total documents: {doc_count}")
        print(f"  Processed: {processed_count}")
        print(f"  Unprocessed: {doc_count - processed_count}")
    
    print("\n" + "=" * 60)
else:
    print("[ERROR] Could not connect to MongoDB")
    print(f"Connection string: {db_manager.connection_string}")

db_manager.disconnect()

