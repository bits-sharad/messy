"""Test database connection"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager

print("=" * 60)
print("Testing MongoDB Connection")
print("=" * 60)

print(f"\nConnection String: {db_manager.connection_string}")
print(f"Database Name: {db_manager.database_name}")

print("\nAttempting connection...")
success = db_manager.connect()

if success or db_manager.is_connected():
    print("\n[OK] Connection successful!")
    db = db_manager.get_database()
    
    # Test a query
    try:
        projects_count = db.projects.count_documents({})
        jobs_count = db.jobs.count_documents({})
        print(f"\nData in database:")
        print(f"  Projects: {projects_count}")
        print(f"  Jobs: {jobs_count}")
    except Exception as e:
        print(f"\n[WARNING] Could not query database: {e}")
else:
    print("\n[FAILED] Could not connect to MongoDB")
    print("\nTroubleshooting:")
    print("  1. Is MongoDB running? (check with: mongosh)")
    print("  2. Is the connection string correct?")
    print("  3. Try: mongosh mongodb://localhost:27017/")

print("\n" + "=" * 60)

