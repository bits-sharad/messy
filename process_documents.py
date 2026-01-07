"""Script to process all documents from job_documents collection"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.database.connection import db_manager
from apps.services.document_service import DocumentService
from apps.ai.services.rag_service import RAGService


async def main():
    """Process all documents from job_documents collection"""
    print("=" * 60)
    print("Document Processing Script")
    print("=" * 60)
    
    # Connect to database
    print("\n1. Connecting to MongoDB...")
    db_manager.connect()
    
    if not db_manager.is_connected():
        print("[ERROR] Failed to connect to MongoDB")
        print("Please ensure MongoDB is running at mongodb://localhost:27017/")
        return
    
    print("[OK] Connected to MongoDB")
    
    # Initialize services
    print("\n2. Initializing services...")
    try:
        rag_service = RAGService()
        document_service = DocumentService(rag_service=rag_service)
        print("[OK] Services initialized")
    except Exception as e:
        print(f"[WARNING] Could not initialize RAG service: {e}")
        print("Will process documents without embeddings")
        document_service = DocumentService(rag_service=None)
    
    # Process all documents
    print("\n3. Processing documents from job_documents collection...")
    print("-" * 60)
    
    result = await document_service.process_all_documents(
        job_id=None,  # Process all jobs
        generate_embeddings=True
    )
    
    # Display results
    print("\n4. Processing Results:")
    print("-" * 60)
    print(f"Total documents found: {result.get('total', 0)}")
    print(f"Successfully processed: {result.get('processed', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    
    if result.get("results"):
        print("\n5. Individual Results:")
        print("-" * 60)
        for item in result["results"]:
            status = "[OK]" if item.get("success") else "[FAILED]"
            doc_id = item.get("document_id", "unknown")
            error = item.get("error", "")
            print(f"{status} Document {doc_id}")
            if error:
                print(f"      Error: {error}")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Processing cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.disconnect()

