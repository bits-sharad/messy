"""Document processing service for job documents"""
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

from apps.database.connection import db_manager
from apps.services.pdf_service import get_pdf_service
from apps.ai.services.rag_service import RAGService


class DocumentService:
    """Service for processing and managing job documents"""
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        """
        Initialize document service
        
        Args:
            rag_service: Optional RAGService instance for embeddings
        """
        self.pdf_service = get_pdf_service()
        self.rag_service = rag_service
        self.collection_name = "job_documents"
        self.processed_collection_name = "processed_documents"
    
    def get_database(self):
        """Get MongoDB database instance"""
        return db_manager.get_database()
    
    async def process_document(
        self, 
        document_id: str, 
        job_id: Optional[str] = None,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Process a document from job_documents collection:
        1. Extract text from PDF
        2. Generate embeddings
        3. Store processed content
        
        Args:
            document_id: Document ID from job_documents collection
            job_id: Optional job ID to link the document
            generate_embeddings: Whether to generate embeddings
            
        Returns:
            Dictionary with processing result
        """
        try:
            db = self.get_database()
            job_documents_collection = db[self.collection_name]
            processed_collection = db[self.processed_collection_name]
            
            # Fetch document from job_documents collection
            document = job_documents_collection.find_one({"_id": ObjectId(document_id)})
            if not document:
                return {
                    "success": False,
                    "error": f"Document {document_id} not found in {self.collection_name}"
                }
            
            # Extract PDF content
            pdf_content = document.get("content") or document.get("file_content")
            if not pdf_content:
                return {
                    "success": False,
                    "error": "No PDF content found in document"
                }
            
            # Extract text from PDF
            pdf_result = self.pdf_service.extract_text_from_bytes(
                pdf_content if isinstance(pdf_content, bytes) else pdf_content.encode(),
                use_advanced=True
            )
            
            if not pdf_result.get("success"):
                return {
                    "success": False,
                    "error": f"PDF extraction failed: {pdf_result.get('error')}"
                }
            
            extracted_text = pdf_result.get("content", "")
            pdf_metadata = pdf_result.get("metadata", {})
            
            # Generate embeddings if requested
            embedding = None
            if generate_embeddings and self.rag_service:
                try:
                    embedding = self.rag_service.generate_embedding(extracted_text)
                except Exception as e:
                    print(f"Warning: Failed to generate embedding: {e}")
            
            # Create processed document
            processed_doc = {
                "_id": ObjectId(),
                "original_document_id": str(document.get("_id")),
                "job_id": job_id or document.get("job_id"),
                "project_id": document.get("project_id"),
                "title": document.get("title") or pdf_metadata.get("title", "Untitled"),
                "extracted_text": extracted_text,
                "pdf_metadata": pdf_metadata,
                "embedding": embedding,  # Store embedding in MongoDB
                "content_length": len(extracted_text),
                "word_count": len(extracted_text.split()),
                "processing_metadata": {
                    "processed_at": datetime.utcnow(),
                    "embedding_model": "all-MiniLM-L6-v2" if embedding else None,
                    "embedding_dim": len(embedding) if embedding else None
                },
                "status": "processed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store in processed_documents collection
            result = processed_collection.insert_one(processed_doc)
            
            # Update original document with processing status
            job_documents_collection.update_one(
                {"_id": ObjectId(document_id)},
                {
                    "$set": {
                        "processed": True,
                        "processed_at": datetime.utcnow(),
                        "processed_document_id": str(processed_doc["_id"])
                    }
                }
            )
            
            return {
                "success": True,
                "processed_document_id": str(processed_doc["_id"]),
                "original_document_id": document_id,
                "content_length": len(extracted_text),
                "word_count": len(extracted_text.split()),
                "has_embedding": embedding is not None,
                "document": processed_doc
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_all_documents(
        self,
        job_id: Optional[str] = None,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Process all unprocessed documents from job_documents collection
        
        Args:
            job_id: Optional filter by job_id
            generate_embeddings: Whether to generate embeddings
            
        Returns:
            Dictionary with processing results
        """
        try:
            db = self.get_database()
            collection = db[self.collection_name]
            
            # Find unprocessed documents
            query = {"processed": {"$ne": True}}
            if job_id:
                query["job_id"] = job_id
            
            documents = list(collection.find(query))
            
            results = {
                "total": len(documents),
                "processed": 0,
                "failed": 0,
                "results": []
            }
            
            for doc in documents:
                doc_id = str(doc.get("_id"))
                result = await self.process_document(
                    document_id=doc_id,
                    job_id=job_id or doc.get("job_id"),
                    generate_embeddings=generate_embeddings
                )
                
                if result.get("success"):
                    results["processed"] += 1
                else:
                    results["failed"] += 1
                
                results["results"].append({
                    "document_id": doc_id,
                    "success": result.get("success"),
                    "error": result.get("error")
                })
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_document_content(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Get processed document content for a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Dictionary with document content
        """
        try:
            db = self.get_database()
            processed_collection = db[self.processed_collection_name]
            
            # Find processed documents for this job
            documents = list(processed_collection.find({
                "job_id": job_id,
                "status": "processed"
            }))
            
            if not documents:
                return {
                    "has_documents": False,
                    "documents": [],
                    "total_content": ""
                }
            
            # Combine all document content
            all_content = []
            for doc in documents:
                all_content.append({
                    "id": str(doc.get("_id")),
                    "title": doc.get("title", "Untitled"),
                    "extracted_text": doc.get("extracted_text", ""),
                    "content_length": doc.get("content_length", 0),
                    "word_count": doc.get("word_count", 0),
                    "pdf_metadata": doc.get("pdf_metadata", {}),
                    "has_embedding": doc.get("embedding") is not None
                })
            
            combined_text = "\n\n".join([d["extracted_text"] for d in all_content])
            
            return {
                "has_documents": True,
                "document_count": len(documents),
                "documents": all_content,
                "total_content": combined_text,
                "total_content_length": len(combined_text),
                "total_word_count": len(combined_text.split())
            }
            
        except Exception as e:
            return {
                "has_documents": False,
                "error": str(e),
                "documents": []
            }
    
    async def get_documents_for_project(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Get all processed documents for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with documents grouped by job
        """
        try:
            db = self.get_database()
            processed_collection = db[self.processed_collection_name]
            
            # Find processed documents for this project
            documents = list(processed_collection.find({
                "project_id": project_id,
                "status": "processed"
            }))
            
            # Group by job_id
            documents_by_job = {}
            for doc in documents:
                job_id = doc.get("job_id", "unknown")
                if job_id not in documents_by_job:
                    documents_by_job[job_id] = []
                
                documents_by_job[job_id].append({
                    "id": str(doc.get("_id")),
                    "title": doc.get("title", "Untitled"),
                    "extracted_text": doc.get("extracted_text", ""),
                    "content_length": doc.get("content_length", 0),
                    "word_count": doc.get("word_count", 0)
                })
            
            return {
                "project_id": project_id,
                "has_documents": len(documents) > 0,
                "document_count": len(documents),
                "documents_by_job": documents_by_job
            }
            
        except Exception as e:
            return {
                "project_id": project_id,
                "has_documents": False,
                "error": str(e),
                "documents_by_job": {}
            }

