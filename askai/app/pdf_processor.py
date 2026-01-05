"""
PDF Processing Pipeline for Snaphomz
Handles PDF upload, text extraction, chunking, and embedding generation
"""

import os
from typing import List, Dict, Any
import hashlib
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None


class PDFProcessor:
    """
    Processes uploaded PDFs for RAG pipeline
    """
    
    def __init__(self, storage_path: str = "./data/pdfs"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
    def save_pdf(self, uploaded_file, user_id: str) -> Dict[str, Any]:
        """
        Save uploaded PDF to storage
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            user_id: User identifier
            
        Returns:
            Dict with file metadata
        """
        # Generate unique file ID
        file_content = uploaded_file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        
        # Create user directory
        user_dir = os.path.join(self.storage_path, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save file
        filename = f"{file_hash}_{uploaded_file.name}"
        filepath = os.path.join(user_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(file_content)
        
        return {
            "file_id": file_hash,
            "filename": uploaded_file.name,
            "filepath": filepath,
            "size": len(file_content),
            "uploaded_at": datetime.now().isoformat(),
            "user_id": user_id
        }
    
    def extract_text(self, filepath: str) -> str:
        """
        Extract text from PDF
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Extracted text
        """
        if pdfplumber is None:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
        
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if RecursiveCharacterTextSplitter is None:
            # Fallback: simple chunking
            chunks = []
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunks.append(text[i:i + chunk_size])
            return chunks
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        return text_splitter.split_text(text)
    
    def is_valuable_pdf(self, text: str) -> bool:
        """
        Determine if PDF contains valuable information
        
        Args:
            text: Extracted text
            
        Returns:
            True if valuable, False otherwise
        """
        # Check for inspection-related keywords
        valuable_keywords = [
            "inspection", "report", "condition", "repair",
            "foundation", "roof", "electrical", "plumbing",
            "hvac", "structural", "defect", "damage",
            "appraisal", "assessment", "disclosure"
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in valuable_keywords if keyword in text_lower)
        
        # Consider valuable if has 3+ keywords and reasonable length
        return keyword_count >= 3 and len(text) > 500
    
    def process_pdf(self, uploaded_file, user_id: str) -> Dict[str, Any]:
        """
        Complete PDF processing pipeline
        
        Args:
            uploaded_file: Streamlit UploadedFile
            user_id: User identifier
            
        Returns:
            Processing result with metadata and chunks
        """
        # Step 1: Save PDF
        metadata = self.save_pdf(uploaded_file, user_id)
        
        # Step 2: Extract text
        text = self.extract_text(metadata["filepath"])
        metadata["text_length"] = len(text)
        
        # Step 3: Value check
        is_valuable = self.is_valuable_pdf(text)
        metadata["is_valuable"] = is_valuable
        
        if not is_valuable:
            metadata["status"] = "stored_not_processed"
            metadata["chunks"] = []
            return metadata
        
        # Step 4: Chunk text
        chunks = self.chunk_text(text)
        metadata["chunks"] = chunks
        metadata["chunk_count"] = len(chunks)
        metadata["status"] = "processed"
        
        return metadata
