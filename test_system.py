"""
Test Script for Policy RAG System
Verifies all components work correctly
"""

import os
import sys
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from query_engine import RAGQueryEngine


def test_document_processor():
    """Test document processing"""
    print("\n" + "="*60)
    print("TEST 1: Document Processor")
    print("="*60)
    
    try:
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        
        # Test with sample text
        sample_text = """
        Employee Expense Policy
        
        Section 1: General Guidelines
        All employees must submit expense reports within 30 days of incurring expenses.
        Receipts are required for all expenses over $25.
        
        Section 2: Eligible Expenses
        The following expenses are eligible for reimbursement:
        - Transportation costs for business travel
        - Meals during business trips (up to $50 per day)
        - Office supplies necessary for work
        
        Section 3: Approval Process
        All expense reports must be approved by your direct manager.
        Reports over $1000 require additional approval from finance department.
        """
        
        # Test chunking
        metadata = {
            "filename": "test_policy.pdf",
            "department": "Finance",
            "region": "Global",
            "policy_type": "Policy"
        }
        
        chunks = processor.chunk_text(sample_text, metadata)
        
        print(f"✅ Created {len(chunks)} chunks from sample text")
        print(f"   First chunk preview: {chunks[0]['text'][:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_vector_store():
    """Test vector store operations"""
    print("\n" + "="*60)
    print("TEST 2: Vector Store")
    print("="*60)
    
    try:
        # Initialize vector store
        vector_store = VectorStoreManager(
            collection_name="test_collection",
            persist_directory="./test_chroma_db"
        )
        
        # Add test documents
        test_chunks = [
            {
                "text": "Employees must submit expense reports within 30 days. Receipts required for expenses over $25.",
                "metadata": {
                    "filename": "expense_policy.pdf",
                    "department": "Finance",
                    "region": "Global",
                    "policy_type": "Policy"
                }
            },
            {
                "text": "Business travel must be booked through the approved vendor portal. Get manager approval first.",
                "metadata": {
                    "filename": "travel_policy.pdf",
                    "department": "Finance",
                    "region": "Global",
                    "policy_type": "Procedure"
                }
            },
            {
                "text": "Remote work is allowed up to 3 days per week. Employees must maintain core working hours.",
                "metadata": {
                    "filename": "remote_work_policy.pdf",
                    "department": "Human Resources",
                    "region": "Global",
                    "policy_type": "Policy"
                }
            }
        ]
        
        vector_store.add_documents(test_chunks)
        print(f"✅ Added {len(test_chunks)} test documents")
        
        # Test search
        results = vector_store.search("How do I submit expenses?", n_results=2)
        print(f"✅ Search returned {len(results['documents'][0])} results")
        print(f"   Top result: {results['documents'][0][0][:80]}...")
        
        # Clean up
        vector_store.delete_collection()
        print("✅ Cleaned up test collection")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_query_engine():
    """Test RAG query engine"""
    print("\n" + "="*60)
    print("TEST 3: Query Engine (with Claude API)")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found in environment")
        print("   Set it in .env file or environment variable")
        print("   Skipping this test...")
        return None
    
    try:
        # Initialize vector store with test data
        vector_store = VectorStoreManager(
            collection_name="test_collection",
            persist_directory="./test_chroma_db"
        )
        
        test_chunks = [
            {
                "text": "Employees must submit expense reports within 30 days of incurring expenses. All expenses over $25 require receipts. Submit reports through the finance portal.",
                "metadata": {
                    "filename": "expense_policy.pdf",
                    "department": "Finance",
                    "region": "Global",
                    "policy_type": "Policy"
                }
            },
            {
                "text": "Travel bookings must be made through our approved vendor portal. Advance approval from your manager is required for all business travel. Economy class is required for flights under 6 hours.",
                "metadata": {
                    "filename": "travel_policy.pdf",
                    "department": "Finance", 
                    "region": "Global",
                    "policy_type": "Procedure"
                }
            }
        ]
        
        vector_store.add_documents(test_chunks)
        
        # Initialize query engine
        query_engine = RAGQueryEngine(vector_store, api_key=api_key)
        
        # Test query
        print("\nAsking: 'What is the deadline for submitting expense reports?'")
        result = query_engine.query(
            "What is the deadline for submitting expense reports?",
            n_results=2
        )
        
        print(f"\n✅ Received answer from Claude:")
        print(f"   {result['answer'][:200]}...")
        print(f"\n   Sources: {len(result['sources'])} policies referenced")
        
        # Clean up
        vector_store.delete_collection()
        print("\n✅ Query engine test completed")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("WATER.ORG POLICY RAG SYSTEM - TEST SUITE")
    print("="*60)
    
    results = {
        "Document Processor": test_document_processor(),
        "Vector Store": test_vector_store(),
        "Query Engine": test_query_engine()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        
        print(f"{test_name}: {status}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Add your policy PDFs to ./policies directory")
        print("2. Run: python ingest.py ./policies")
        print("3. Run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    run_all_tests()
