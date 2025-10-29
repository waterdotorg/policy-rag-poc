"""
Vector Store Manager for Policy RAG System
Handles embedding generation and vector storage with ChromaDB
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import os


class VectorStoreManager:
    """Manage document embeddings and vector search"""
    
    def __init__(
        self, 
        collection_name: str = "policy_documents",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store
        
        Args:
            collection_name: Name for the document collection
            persist_directory: Directory to persist the database
            embedding_model: Sentence transformer model for embeddings
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Water.org policy documents"}
        )
        
        print(f"Vector store initialized. Current document count: {self.collection.count()}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
        """
        if not chunks:
            print("No chunks to add")
            return
        
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate IDs
        ids = [f"chunk_{i}_{chunk['metadata'].get('filename', 'unknown')}" 
               for i, chunk in enumerate(chunks)]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Successfully added {len(chunks)} chunks. Total count: {self.collection.count()}")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"department": "HR"})
            
        Returns:
            Dictionary with documents, metadata, and distances
        """
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]
        
        # Build where clause for filtering
        where = filter_metadata if filter_metadata else None
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_collection(self) -> None:
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection_name)
        print(f"Collection '{self.collection_name}' deleted")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        
        # Get sample of metadata to show what fields are available
        sample_results = self.collection.get(limit=1)
        sample_metadata = sample_results['metadatas'][0] if sample_results['metadatas'] else {}
        
        return {
            "total_chunks": count,
            "collection_name": self.collection_name,
            "sample_metadata_fields": list(sample_metadata.keys())
        }
    
    def list_unique_values(self, metadata_field: str) -> List[str]:
        """
        Get unique values for a metadata field
        
        Args:
            metadata_field: Field name (e.g., 'department', 'region')
            
        Returns:
            List of unique values
        """
        # Get all documents
        all_docs = self.collection.get()
        
        # Extract unique values
        values = set()
        for metadata in all_docs['metadatas']:
            if metadata_field in metadata:
                values.add(metadata[metadata_field])
        
        return sorted(list(values))


# Example usage and testing
if __name__ == "__main__":
    # Initialize vector store
    vector_store = VectorStoreManager()
    
    # Test with sample chunks
    test_chunks = [
        {
            "text": "Employees must submit expense reports within 30 days of incurring expenses.",
            "metadata": {
                "filename": "expense_policy.pdf",
                "department": "Finance",
                "region": "Global",
                "policy_type": "Policy"
            }
        },
        {
            "text": "Travel bookings should be made through the approved vendor portal.",
            "metadata": {
                "filename": "travel_policy.pdf",
                "department": "Finance",
                "region": "Global",
                "policy_type": "Procedure"
            }
        }
    ]
    
    # Uncomment to test adding documents
    # vector_store.add_documents(test_chunks)
    
    # Test search
    # results = vector_store.search("How do I submit expenses?", n_results=2)
    # print("Search results:", results)
    
    print("Vector Store Manager initialized successfully")
