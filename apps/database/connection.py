"""Database connection manager"""
import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


class DatabaseManager:
    """Manager for MongoDB database connections"""
    
    def __init__(self):
        """Initialize database manager"""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connection_string = os.getenv(
            "MONGODB_URL", 
            os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        )
        self.database_name = os.getenv("MONGODB_DATABASE", "job_matching_db")
    
    def connect(self):
        """Establish database connection"""
        try:
            # Reset connection if already exists
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
            
            print(f"Attempting to connect to MongoDB...")
            print(f"  Connection string: {self.connection_string}")
            print(f"  Database name: {self.database_name}")
            
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout (increased)
            )
            # Test connection
            self.client.server_info()
            self.db = self.client[self.database_name]
            print(f"[OK] Connected to MongoDB database: {self.database_name}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")
            print(f"  Connection string: {self.connection_string}")
            print("  The application will start but database operations will fail.")
            print("  To fix:")
            print("    1. Ensure MongoDB is running: mongod (or net start MongoDB on Windows)")
            print("    2. Check connection string is correct")
            print("    3. Verify firewall isn't blocking port 27017")
            # Set to None to indicate failure
            self.client = None
            self.db = None
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            try:
                self.client.close()
                print("Disconnected from MongoDB")
            except Exception as e:
                print(f"Error disconnecting from MongoDB: {e}")
            finally:
                self.client = None
                self.db = None
    
    def get_database(self) -> Database:
        """
        Get database instance
        
        Returns:
            MongoDB Database instance
            
        Raises:
            RuntimeError: If database is not connected
        """
        if self.db is None:
            if self.client is None:
                raise RuntimeError(
                    "Database not connected. Call connect() first. "
                    "If MongoDB is not available, ensure MongoDB is running or set MONGODB_URL environment variable."
                )
            self.db = self.client[self.database_name]
        return self.db
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if self.client:
                self.client.server_info()
                return True
        except Exception:
            pass
        return False


# Singleton instance
db_manager = DatabaseManager()

