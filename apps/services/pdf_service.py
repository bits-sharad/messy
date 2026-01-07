"""PDF processing service for extracting text from PDF files"""
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import io

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("Warning: PyPDF2 not installed. PDF processing will be limited.")

try:
    from pdfplumber import PDF
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("Warning: pdfplumber not installed. Advanced PDF processing will be limited.")


class PDFService:
    """Service for processing PDF files and extracting text content"""
    
    def __init__(self):
        """Initialize PDF service"""
        self.supported_formats = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: str, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to PDF file (can be file path or base64 encoded content)
            use_advanced: Whether to use pdfplumber (better) or PyPDF2 (basic)
            
        Returns:
            Dictionary with extracted content and metadata
        """
        if not HAS_PYPDF2 and not HAS_PDFPLUMBER:
            raise ImportError(
                "No PDF processing library available. "
                "Please install PyPDF2 or pdfplumber: pip install PyPDF2 pdfplumber"
            )
        
        try:
            # Check if pdf_path is a file path or needs to be read
            if os.path.exists(pdf_path):
                # It's a file path
                with open(pdf_path, 'rb') as file:
                    pdf_content = file.read()
            else:
                # Assume it's already PDF content (bytes)
                pdf_content = pdf_path if isinstance(pdf_path, bytes) else pdf_path.encode()
            
            # Use pdfplumber if available and requested (better quality)
            if use_advanced and HAS_PDFPLUMBER:
                return self._extract_with_pdfplumber(pdf_content)
            elif HAS_PYPDF2:
                return self._extract_with_pypdf2(pdf_content)
            else:
                raise ImportError("No PDF processing library available")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {}
            }
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract text using pdfplumber (better quality)"""
        from pdfplumber import PDF
        
        metadata = {}
        full_text = []
        
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf = PDF(pdf_file)
            
            metadata = {
                "total_pages": len(pdf.pages),
                "method": "pdfplumber"
            }
            
            # Extract text from each page
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text.append(f"--- Page {i + 1} ---\n{page_text}")
            
            # Extract metadata if available
            if pdf.metadata:
                metadata.update({
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                })
            
            content = "\n\n".join(full_text)
            
            return {
                "success": True,
                "content": content,
                "metadata": metadata,
                "content_length": len(content),
                "word_count": len(content.split())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {}
            }
    
    def _extract_with_pypdf2(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract text using PyPDF2 (basic)"""
        import PyPDF2
        
        metadata = {}
        full_text = []
        
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = {
                "total_pages": len(pdf_reader.pages),
                "method": "PyPDF2"
            }
            
            # Extract metadata if available
            if pdf_reader.metadata:
                metadata.update({
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                })
            
            # Extract text from each page
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text.append(f"--- Page {i + 1} ---\n{page_text}")
                except Exception as e:
                    print(f"Warning: Could not extract text from page {i + 1}: {e}")
            
            content = "\n\n".join(full_text)
            
            return {
                "success": True,
                "content": content,
                "metadata": metadata,
                "content_length": len(content),
                "word_count": len(content.split())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {}
            }
    
    def extract_text_from_bytes(self, pdf_bytes: bytes, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Extract text from PDF bytes directly
        
        Args:
            pdf_bytes: PDF file content as bytes
            use_advanced: Whether to use advanced extraction
            
        Returns:
            Dictionary with extracted content
        """
        return self.extract_text_from_pdf(pdf_bytes, use_advanced)
    
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if file is a PDF"""
        return Path(file_path).suffix.lower() == '.pdf'


# Singleton instance
_pdf_service: Optional[PDFService] = None


def get_pdf_service() -> PDFService:
    """Get singleton instance of PDF service"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service

