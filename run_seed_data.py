"""Run this script to seed dummy data"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.seed_data import main

if __name__ == "__main__":
    print("Starting data seeding...")
    asyncio.run(main())

