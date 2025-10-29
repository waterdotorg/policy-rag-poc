"""
Bulk Document Ingestion Script
Load policies from a directory with metadata from a CSV file
"""

import os
import pandas as pd
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_policies_from_csv(pdf_directory: str, metadata_csv: str):
    """
    Load policies with metadata from CSV
    
    CSV format:
    filename,department,region,policy_type,effective_date,description
    expense_policy.pdf,Finance,Global,Policy,2024-01-01,Travel and expense reimbursement
    travel_procedure.pdf,Finance,Global,Procedure,2024-01-01,How to book travel
    
    Args:
        pdf_directory: Directory containing PDF files
        metadata_csv: Path to CSV file with metadata
    """
    # Read metadata
    try:
        metadata_df = pd.read_csv(metadata_csv)
        print(f"Loaded metadata for {len(metadata_df)} documents")
    except Exception as e:
        print(f"Error reading metadata CSV: {e}")
        return
    
    # Initialize components
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    vector_store = VectorStoreManager(
        collection_name="water_org_policies",
        persist_directory="./chroma_db"
    )
    
    # Process each document
    all_chunks = []
    
    for _, row in metadata_df.iterrows():
        filename = row['filename']
        pdf_path = os.path.join(pdf_directory, filename)
        
        if not os.path.exists(pdf_path):
            print(f"Warning: File not found: {pdf_path}")
            continue
        
        # Build metadata dictionary
        metadata = {
            "department": row.get('department', ''),
            "region": row.get('region', 'Global'),
            "policy_type": row.get('policy_type', 'Policy'),
            "effective_date": row.get('effective_date', ''),
            "description": row.get('description', '')
        }
        
        # Process document
        chunks = processor.process_document(pdf_path, metadata)
        all_chunks.extend(chunks)
    
    # Add all chunks to vector store
    if all_chunks:
        vector_store.add_documents(all_chunks)
        print(f"\n✅ Successfully indexed {len(all_chunks)} chunks from {len(metadata_df)} documents")
        
        # Print stats
        stats = vector_store.get_collection_stats()
        print(f"Total documents in database: {stats['total_chunks']}")
    else:
        print("No documents were processed")


def simple_ingest(pdf_directory: str, default_metadata: dict = None):
    """
    Simple ingestion without CSV - applies same metadata to all PDFs in directory
    
    Args:
        pdf_directory: Directory containing PDF files
        default_metadata: Metadata to apply to all documents
    """
    if default_metadata is None:
        default_metadata = {
            "department": "General",
            "region": "Global",
            "policy_type": "Policy"
        }
    
    # Initialize components
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    vector_store = VectorStoreManager(
        collection_name="water_org_policies",
        persist_directory="./chroma_db"
    )
    
    # Get all PDFs
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Build metadata map
    metadata_map = {filename: default_metadata for filename in pdf_files}
    
    # Process all documents
    chunks = processor.process_directory(pdf_directory, metadata_map)
    
    # Add to vector store
    if chunks:
        vector_store.add_documents(chunks)
        print(f"\n✅ Successfully indexed {len(chunks)} chunks from {len(pdf_files)} documents")
        
        # Print stats
        stats = vector_store.get_collection_stats()
        print(f"Total documents in database: {stats['total_chunks']}")
    else:
        print("No documents were processed")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Water.org Policy RAG - Document Ingestion")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  Simple ingestion:")
        print("    python ingest.py <pdf_directory>")
        print("\n  With metadata CSV:")
        print("    python ingest.py <pdf_directory> <metadata_csv>")
        print("\nExample:")
        print("    python ingest.py ./policies")
        print("    python ingest.py ./policies ./policies_metadata.csv")
        sys.exit(1)
    
    pdf_dir = sys.argv[1]
    
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory not found: {pdf_dir}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        # Ingest with CSV metadata
        metadata_csv = sys.argv[2]
        if not os.path.exists(metadata_csv):
            print(f"Error: Metadata CSV not found: {metadata_csv}")
            sys.exit(1)
        
        load_policies_from_csv(pdf_dir, metadata_csv)
    else:
        # Simple ingestion
        print("\nNo metadata CSV provided. Using default metadata for all documents.")
        print("Department: General, Region: Global, Type: Policy\n")
        
        simple_ingest(pdf_dir)
