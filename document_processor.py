"""
Document Processor for Policy RAG System
Handles PDF extraction, chunking, and metadata management
"""

import os
from typing import List, Dict, Any
from pypdf import PdfReader
import re


class DocumentProcessor:
    """Process PDF documents into chunks with metadata"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor
        
        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,;:!()?\'\"\/]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence
            if end < len(text):
                # Look for sentence endings (., !, ?) within the next 100 chars
                search_end = min(end + 100, len(text))
                sentence_end = max(
                    text.rfind('. ', end, search_end),
                    text.rfind('! ', end, search_end),
                    text.rfind('? ', end, search_end)
                )
                if sentence_end > end:
                    end = sentence_end + 1
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                        "start_char": start,
                        "end_char": end
                    }
                }
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_document(
        self, 
        pdf_path: str, 
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single PDF document into chunks
        
        Args:
            pdf_path: Path to PDF file
            metadata: Additional metadata (department, region, type, etc.)
            
        Returns:
            List of document chunks with metadata
        """
        if metadata is None:
            metadata = {}
        
        # Add file information to metadata
        filename = os.path.basename(pdf_path)
        metadata["filename"] = filename
        metadata["source"] = pdf_path
        
        # Extract and clean text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Warning: No text extracted from {filename}")
            return []
        
        cleaned_text = self.clean_text(text)
        
        # Create chunks
        chunks = self.chunk_text(cleaned_text, metadata)
        
        print(f"Processed {filename}: {len(chunks)} chunks created")
        return chunks
    
    def process_directory(
        self, 
        directory_path: str,
        metadata_map: Dict[str, Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all PDF files in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            metadata_map: Dictionary mapping filenames to metadata
            
        Returns:
            List of all document chunks
        """
        if metadata_map is None:
            metadata_map = {}
        
        all_chunks = []
        
        # Find all PDF files
        pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
        
        print(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            
            # Get metadata for this file
            file_metadata = metadata_map.get(pdf_file, {})
            
            # Process document
            chunks = self.process_document(pdf_path, file_metadata)
            all_chunks.extend(chunks)
        
        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


# Example usage and testing
if __name__ == "__main__":
    # Example: Process a single document
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    
    # Define metadata for testing
    test_metadata = {
        "department": "Human Resources",
        "region": "Global",
        "policy_type": "Policy",
        "effective_date": "2024-01-01"
    }
    
    # This would process a real PDF - for testing you'd provide an actual path
    # chunks = processor.process_document("path/to/policy.pdf", test_metadata)
    
    print("Document Processor initialized successfully")
