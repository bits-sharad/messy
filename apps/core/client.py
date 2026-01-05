"""Core API Client for metadata operations"""
from typing import Dict, Any, List, Optional
from bson import ObjectId
from datetime import datetime

from apps.database.connection import db_manager


class CoreAPIClient:
    """Client for interacting with metadata storage"""
    
    def __init__(self):
        """Initialize the Core API Client"""
        self._db = None
    
    def _get_db(self):
        """Get database instance"""
        if self._db is None:
            self._db = db_manager.get_database()
        return self._db
    
    async def metadata_put(
        self,
        collection: str,
        document_id: str,
        document: Dict[str, Any],
        upsert: bool = True
    ) -> Dict[str, Any]:
        """
        Store or update a document in the specified collection
        
        Args:
            collection: Collection name (e.g., 'projects')
            document_id: Document ID (MongoDB ObjectId as string)
            document: Document data dictionary
            upsert: If True, create document if it doesn't exist
            
        Returns:
            Dictionary with operation result including document ID
        """
        db = self._get_db()
        coll = db[collection]
        
        # Convert string ID to ObjectId if needed
        if isinstance(document_id, str):
            try:
                obj_id = ObjectId(document_id)
            except Exception:
                obj_id = ObjectId()  # Generate new ID if invalid
        else:
            obj_id = document_id
        
        # Ensure _id is in document (use ObjectId for MongoDB)
        document["_id"] = obj_id
        
        # Add/update timestamps if not present
        if "_id" in document and not document.get("created_at"):
            # Check if document exists
            existing = coll.find_one({"_id": obj_id})
            if existing:
                document["created_at"] = existing.get("created_at", datetime.utcnow())
                document["updated_at"] = datetime.utcnow()
            else:
                document["created_at"] = datetime.utcnow()
                document["updated_at"] = datetime.utcnow()
        elif not document.get("created_at"):
            document["created_at"] = datetime.utcnow()
            document["updated_at"] = datetime.utcnow()
        else:
            document["updated_at"] = datetime.utcnow()
        
        if upsert:
            coll.replace_one({"_id": obj_id}, document, upsert=True)
        else:
            coll.insert_one(document)
        
        return {
            "id": str(obj_id),
            "success": True,
            "document": document
        }
    
    async def metadata_get(
        self,
        collection: str,
        document_id: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve document(s) from the specified collection
        
        Args:
            collection: Collection name (e.g., 'projects')
            document_id: Specific document ID to retrieve (optional)
            query: Query filter dictionary (optional)
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            
        Returns:
            Dictionary with retrieved document(s) or list of documents
        """
        db = self._get_db()
        coll = db[collection]
        
        if document_id:
            # Get single document by ID
            try:
                obj_id = ObjectId(document_id)
                doc = coll.find_one({"_id": obj_id})
                if doc:
                    # Convert ObjectId to string for JSON serialization
                    doc["_id"] = str(doc["_id"])
                    return {
                        "success": True,
                        "document": doc,
                        "count": 1
                    }
                else:
                    return {
                        "success": False,
                        "document": None,
                        "count": 0
                    }
            except Exception as e:
                return {
                    "success": False,
                    "document": None,
                    "count": 0,
                    "error": str(e)
                }
        else:
            # Get multiple documents with query
            query = query or {}
            
            # Convert string IDs to ObjectId if present in query
            if "_id" in query and isinstance(query["_id"], str):
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    pass
            
            cursor = coll.find(query).skip(skip).limit(limit)
            docs = list(cursor)
            
            # Convert ObjectIds to strings
            for doc in docs:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            
            return {
                "success": True,
                "documents": docs,
                "count": len(docs)
            }
    
    async def metadata_delete(
        self,
        collection: str,
        document_id: str,
        hard_delete: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a document from the specified collection
        
        Args:
            collection: Collection name
            document_id: Document ID to delete
            hard_delete: If False, perform soft delete (set deleted flag)
            
        Returns:
            Dictionary with operation result
        """
        db = self._get_db()
        coll = db[collection]
        
        try:
            obj_id = ObjectId(document_id)
            
            if hard_delete:
                result = coll.delete_one({"_id": obj_id})
            else:
                # Soft delete: set deleted_at timestamp
                result = coll.update_one(
                    {"_id": obj_id},
                    {"$set": {"deleted_at": datetime.utcnow(), "status": "archived"}}
                )
            
            return {
                "success": result.deleted_count > 0 or result.modified_count > 0,
                "id": document_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def metadata_count(
        self,
        collection: str,
        query: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents in collection matching query"""
        db = self._get_db()
        coll = db[collection]
        query = query or {}
        return coll.count_documents(query)

