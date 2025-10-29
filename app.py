"""
Streamlit Chat Interface for Policy RAG System - Password Protected
Web-based chat interface for querying organizational policies
"""

import streamlit as st
import os
from pathlib import Path
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from query_engine import RAGQueryEngine
import hashlib

# Page configuration
st.set_page_config(
    page_title="Water.org Policy Assistant",
    page_icon="waterorg_logo.png", #page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from secrets (you'll add this in Streamlit Cloud)
        correct_password = st.secrets.get("APP_PASSWORD", "waterorg2024")  # Default fallback
        
        # Hash the entered password
        entered_hash = hashlib.sha256(st.session_state["password"].encode()).hexdigest()
        correct_hash = hashlib.sha256(correct_password.encode()).hexdigest()
        
        if entered_hash == correct_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run or password not correct
    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔒 Enter Password to Access Policy Assistant", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("Please enter the password to access the application.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "🔒 Enter Password to Access Policy Assistant", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect. Please try again.")
        return False
    else:
        # Password correct
        return True

# Check password before showing app
if not check_password():
    st.stop()  # Don't continue if password is incorrect

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

if "initialized" not in st.session_state:
    st.session_state.initialized = False


def initialize_system(api_key: str):
    """Initialize the RAG system"""
    try:
        # Initialize vector store
        vector_store = VectorStoreManager(
            collection_name="water_org_policies",
            persist_directory="./chroma_db"
        )
        
        # Initialize query engine
        query_engine = RAGQueryEngine(vector_store, api_key=api_key)
        
        st.session_state.vector_store = vector_store
        st.session_state.query_engine = query_engine
        st.session_state.initialized = True
        
        return True, "System initialized successfully!"
    except Exception as e:
        return False, f"Error initializing system: {str(e)}"


def process_and_index_documents(pdf_directory: str, metadata_map: dict):
    """Process PDFs and add to vector store"""
    try:
        # Initialize document processor
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
        
        # Process documents
        chunks = processor.process_directory(pdf_directory, metadata_map)
        
        if not chunks:
            return False, "No documents were processed"
        
        # Add to vector store
        st.session_state.vector_store.add_documents(chunks)
        
        return True, f"Successfully processed and indexed {len(chunks)} chunks from documents"
    except Exception as e:
        return False, f"Error processing documents: {str(e)}"


# Sidebar
with st.sidebar:
    st.title("💧 Policy Assistant Setup")
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    st.divider()
    
    # Try to get API key from secrets first
    auto_api_key = None
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            auto_api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    
    # Also try environment variable
    if not auto_api_key and "ANTHROPIC_API_KEY" in os.environ:
        auto_api_key = os.environ["ANTHROPIC_API_KEY"]
    
    if auto_api_key:
        st.success("✅ API key loaded from secrets")
        api_key = auto_api_key
        
        # Auto-initialize if not already done
        if not st.session_state.initialized:
            with st.spinner("Initializing..."):
                success, message = initialize_system(api_key)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        # Manual API key input
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Enter your Anthropic API key to use Claude"
        )
        
        if api_key and not st.session_state.initialized:
            if st.button("Initialize System"):
                with st.spinner("Initializing..."):
                    success, message = initialize_system(api_key)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    st.divider()
    
    # Document upload section (only show if initialized)
    if st.session_state.initialized:
        st.subheader("📄 Document Management")
        
        # Show current stats
        stats = st.session_state.vector_store.get_collection_stats()
        st.metric("Documents Indexed", stats['total_chunks'])
        
        with st.expander("Add New Documents"):
            st.write("To add documents, place PDF files in a directory and specify metadata.")
            
            pdf_dir = st.text_input("PDF Directory Path", value="./policies")
            
            st.write("**Default Metadata** (applies to all documents in directory)")
            default_dept = st.text_input("Department", value="")
            default_region = st.text_input("Region", value="Global")
            default_type = st.selectbox("Type", ["Policy", "Procedure"])
            
            if st.button("Process Documents"):
                if os.path.exists(pdf_dir):
                    # Create default metadata map
                    metadata_map = {}
                    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
                    
                    for pdf_file in pdf_files:
                        metadata_map[pdf_file] = {
                            "department": default_dept,
                            "region": default_region,
                            "policy_type": default_type
                        }
                    
                    with st.spinner("Processing documents..."):
                        success, message = process_and_index_documents(pdf_dir, metadata_map)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Directory not found")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Search Filters")
        
        # Try to get unique values for filters
        try:
            departments = st.session_state.vector_store.list_unique_values("department")
            regions = st.session_state.vector_store.list_unique_values("region")
            types = st.session_state.vector_store.list_unique_values("policy_type")
            
            filter_dept = st.multiselect("Department", options=departments)
            filter_region = st.multiselect("Region", options=regions)
            filter_type = st.multiselect("Type", options=types)
            
            # Store filters in session state
            st.session_state.filters = {}
            if filter_dept:
                st.session_state.filters["department"] = filter_dept[0]
            if filter_region:
                st.session_state.filters["region"] = filter_region[0]
            if filter_type:
                st.session_state.filters["policy_type"] = filter_type[0]
        except:
            st.session_state.filters = {}
        
        st.divider()
        
        # Clear conversation
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

# Main chat interface
st.title("💧 Water.org Policy Assistant")
st.caption("Ask questions about organizational policies and procedures")

if not st.session_state.initialized:
    if not auto_api_key:
        st.info("👈 Please enter your Anthropic API key in the sidebar to get started")
    else:
        st.info("⏳ Initializing system...")
else:
    # Check if documents are indexed
    stats = st.session_state.vector_store.get_collection_stats()
    if stats['total_chunks'] == 0:
        st.warning("⚠️ No documents indexed yet. Please add documents using the sidebar.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.write(f"**{source['filename']}**")
                        st.write(f"Department: {source['department']} | Region: {source['region']} | Type: {source['policy_type']}")
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about policies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching policies..."):
                # Get filters
                filters = st.session_state.get("filters", {})
                
                # Query the system
                result = st.session_state.query_engine.query(
                    question=prompt,
                    n_results=5,
                    filter_metadata=filters if filters else None
                )
                
                # Display answer
                st.markdown(result["answer"])
                
                # Display sources
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        for source in result["sources"]:
                            st.write(f"**{source['filename']}**")
                            st.write(f"Department: {source['department']} | Region: {source['region']} | Type: {source['policy_type']}")
                            st.divider()
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"]
        })

# Footer
st.divider()
st.caption("Built with Anthropic Claude, ChromaDB, and Streamlit | 🔒 Password Protected")
