"""
Vector Database Integration for Snaphomz
Handles embedding generation and vector storage using ChromaDB
"""

import os
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None


class VectorStore:
    """
    Manages vector embeddings and retrieval
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        if chromadb is None:
            raise ImportError("chromadb not installed. Run: pip install chromadb")
        
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="snaphomz_documents",
            metadata={"description": "Property inspection and disclosure documents"}
        )
        
        # Initialize embeddings (using Google Gemini for consistency)
        self.embeddings = self._get_embeddings()
    
    def _get_embeddings(self):
        """Get embedding model"""
        if GoogleGenerativeAIEmbeddings:
            try:
                return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            except:
                pass
        
        # Fallback: use ChromaDB's default embeddings
        return None
    
    def add_documents(
        self, 
        chunks: List[str], 
        metadata: Dict[str, Any],
        file_id: str
    ) -> Dict[str, Any]:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks
            metadata: Document metadata
            file_id: Unique file identifier
            
        Returns:
            Result with added document info
        """
        if not chunks:
            return {"status": "skipped", "reason": "no_chunks"}
        
        # Prepare documents and metadata
        documents = chunks
        metadatas = [
            {
                "file_id": file_id,
                "filename": metadata.get("filename", "unknown"),
                "user_id": metadata.get("user_id", "unknown"),
                "chunk_index": i,
                "uploaded_at": metadata.get("uploaded_at", "")
            }
            for i in range(len(chunks))
        ]
        
        # Generate IDs
        ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Generate embeddings if custom model available
        embeddings = None
        if self.embeddings:
            try:
                embeddings = [self.embeddings.embed_query(chunk) for chunk in chunks]
            except:
                embeddings = None
        
        # Add to collection
        if embeddings:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        else:
            # Let ChromaDB generate embeddings
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return {
            "status": "success",
            "chunks_added": len(chunks),
            "file_id": file_id
        }
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            user_id: Optional user filter
            
        Returns:
            List of relevant document chunks
        """
        # Build where filter
        where_filter = None
        if user_id:
            where_filter = {"user_id": user_id}
        
        # Search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results.get('distances') else None
                })
        
        return formatted_results
    
    def delete_user_documents(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all documents for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Deletion result
        """
        # Get all documents for user
        results = self.collection.get(where={"user_id": user_id})
        
        if results and results['ids']:
            self.collection.delete(ids=results['ids'])
            return {"status": "success", "deleted_count": len(results['ids'])}
        
        return {"status": "success", "deleted_count": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }
