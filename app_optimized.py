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
import PyPDF2
import io

# Initialize session state at the very top of your app
if "temp_document" not in st.session_state:
    st.session_state.temp_document = None

if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Page configuration
st.set_page_config(
    page_title="Water.org Policy Assistant",
    page_icon="waterorg_logo.png",
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

if "temp_document" not in st.session_state:
    st.session_state.temp_document = None


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


def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file for temporary use (not indexed)"""
    try:
        import PyPDF2
        import io
        
        # Ensure we're at the start of the file buffer
        uploaded_file.seek(0)
        
        # Read PDF from uploaded file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# Sidebar
with st.sidebar:
    

    st.markdown("# Water.org Policy Assistant")
    st.caption("Ask questions about organizational policies and procedures")


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

st.title("Water.org Policy Assistant")
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
    
    # Temporary document upload for comparison (not indexed)
    st.subheader("📄 Upload Document for Comparison")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a policy document to compare against existing policies (not permanently stored)",
            type=['pdf'],
            key="temp_upload"
        )
    
    with col2:
        if st.session_state.temp_document:
            st.success("✅ Document loaded")
            if st.button("Clear Document"):
                st.session_state.temp_document = None
                st.rerun()
    
    if uploaded_file and st.session_state.temp_document is None:
        st.write("DEBUG: About to extract text...")
        st.write(f"DEBUG: File name: {uploaded_file.name}")
        with st.spinner("Extracting text from PDF..."):            
            text = extract_text_from_pdf(uploaded_file)
            st.write(f"DEBUG: Text extracted, length: {len(text)}")
            if not text.startswith("Error"):
                st.session_state.temp_document = {
                    "filename": uploaded_file.name,
                    "text": text
                }
                st.success(f"✅ Loaded: {uploaded_file.name}")
                st.info("💡 Now ask questions like: 'Does this policy overlap with existing policies?' or 'Are there any contradictions?'")
            else:
                st.error(text)
    
    if st.session_state.temp_document:
        st.info(f"📄 **Current document:** {st.session_state.temp_document['filename']}")
    
    st.divider()
    
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
        # Get filters
        filters = st.session_state.get("filters", {})
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            # Initialize variables
            answer = ""
            sources = []
            
            # If there's a temporary document, do enhanced comparison
            if st.session_state.temp_document:
                with st.spinner("🔍 Analyzing uploaded document..."):
                    uploaded_text = st.session_state.temp_document['text']
                    uploaded_filename = st.session_state.temp_document['filename']
                    
                    # IMPROVED APPROACH: Content-based search with more results
                    # Step 1: Chunk the uploaded document
                    status = st.status("Processing comparison...", expanded=True)
                    status.write("📄 Chunking uploaded document...")
                    
                    uploaded_chunks = []
                    chunk_size = 1000
                    chunk_overlap = 200
                    start = 0
                    while start < len(uploaded_text):
                        end = start + chunk_size
                        uploaded_chunks.append(uploaded_text[start:end])
                        start += chunk_size - chunk_overlap
                    
                    status.write(f"✓ Created {len(uploaded_chunks)} chunks from uploaded document")
                    
                    # Step 2: Search using uploaded doc content (not just the question)
                    status.write("🔎 Searching for similar policies in database...")
                    
                    all_results = []
                    seen_ids = set()
                    
                    # Use first 3 chunks as search queries
                    search_chunks = uploaded_chunks[:min(3, len(uploaded_chunks))]
                    
                    for chunk in search_chunks:
                        # Query using each chunk
                        chunk_results = st.session_state.vector_store.collection.query(
                            query_texts=[chunk],
                            n_results=10,  # Increased from 5 to get more coverage
                            include=['documents', 'metadatas', 'distances'],
                            where=filters if filters else None
                        )
                        
                        # Collect results and deduplicate
                        if chunk_results['ids'] and chunk_results['ids'][0]:
                            for i, doc_id in enumerate(chunk_results['ids'][0]):
                                if doc_id not in seen_ids:
                                    seen_ids.add(doc_id)
                                    all_results.append({
                                        'text': chunk_results['documents'][0][i],
                                        'metadata': chunk_results['metadatas'][0][i],
                                        'distance': chunk_results['distances'][0][i]
                                    })
                    
                    status.write(f"✓ Found {len(all_results)} relevant policy chunks")
                    
                    # Step 3: Sort by similarity and limit to top 20
                    all_results.sort(key=lambda x: x['distance'])
                    top_results = all_results[:20]
                    
                    # Step 4: Group by document for better context
                    status.write("📋 Organizing results by policy document...")
                    
                    policies_by_doc = {}
                    for result in top_results:
                        filename = result['metadata'].get('filename', 'Unknown')
                        if filename not in policies_by_doc:
                            policies_by_doc[filename] = {
                                'chunks': [],
                                'metadata': result['metadata']
                            }
                        policies_by_doc[filename]['chunks'].append(result['text'])
                    
                    status.write(f"✓ Comparing against {len(policies_by_doc)} existing policies")
                    
                    # Check if we found any policies
                    if not policies_by_doc:
                        answer = f"""I analyzed the uploaded document "{uploaded_filename}" but couldn't find any similar existing policies in the database.

This could mean:
- This is a completely new topic not covered by existing policies
- The existing policy database is empty or not yet indexed
- The search terms in the document don't match existing policy content

Would you like to:
1. Upload this as a permanent policy to the database
2. Check if existing policies are properly indexed
3. Ask a more specific question about the document content"""
                        sources = []
                        status.update(label="⚠️ No similar policies found", state="complete")
                    else:
                        # Step 5: Build comprehensive comparison prompt
                        existing_policies_text = ""
                        for filename, data in list(policies_by_doc.items())[:5]:  # Limit to 5 policies to avoid context overflow
                            policy_text = "\n\n".join(data['chunks'])
                            existing_policies_text += f"\n\n=== {filename} ===\n"
                            existing_policies_text += f"Department: {data['metadata'].get('department', 'N/A')}\n"
                            existing_policies_text += f"Region: {data['metadata'].get('region', 'N/A')}\n"
                            existing_policies_text += f"Type: {data['metadata'].get('policy_type', 'N/A')}\n"
                            existing_policies_text += f"Content:\n{policy_text[:2000]}\n"  # Limit each policy to avoid overflow
                        
                        comparison_prompt = f"""You are analyzing a new policy document against existing organizational policies.

NEW POLICY DOCUMENT: {uploaded_filename}
{uploaded_text[:6000]}

EXISTING POLICIES IN DATABASE:
{existing_policies_text}

USER'S QUESTION: {prompt}

Please provide a comprehensive analysis that includes:
1. **Overlaps**: What topics/requirements exist in both the new policy and existing policies?
2. **Contradictions**: Where does the new policy conflict with existing policies? Be specific about what contradicts.
3. **Gaps**: What does the new policy cover that isn't in existing policies?
4. **Redundancies**: Is this new policy necessary or does it duplicate existing policies?
5. **Recommendations**: Should this policy be adopted as-is, merged with existing policies, or modified?

For each finding, cite the specific existing policy name.
"""
                        
                        # Step 6: Query Claude
                        status.write("🤖 Analyzing with Claude...")
                        
                        from anthropic import Anthropic
                        client = Anthropic(api_key=st.session_state.query_engine.api_key)
                        
                        response = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=3000,
                            messages=[
                                {"role": "user", "content": comparison_prompt}
                            ]
                        )
                        
                        answer = response.content[0].text
                        status.update(label="✅ Analysis complete!", state="complete")
                        
                        # Format sources
                        sources = [
                            {
                                'filename': filename,
                                'department': data['metadata'].get('department', 'N/A'),
                                'region': data['metadata'].get('region', 'N/A'),
                                'policy_type': data['metadata'].get('policy_type', 'N/A')
                            }
                            for filename, data in policies_by_doc.items()
                        ]
                
            else:
                # Regular query without uploaded document
                with st.spinner("Searching policies..."):
                    result = st.session_state.query_engine.query(
                        question=prompt,
                        n_results=5,
                        filter_metadata=filters if filters else None
                    )
                    answer = result["answer"]
                    sources = result["sources"]
            
            # Display answer (moved outside if/else so it always runs)
            st.markdown(answer)
            
            # Display sources
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.write(f"**{source['filename']}**")
                        st.write(f"Department: {source['department']} | Region: {source['region']} | Type: {source['policy_type']}")
                        st.divider()
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

# Footer
st.divider()
st.caption("Built with Anthropic Claude, ChromaDB, and Streamlit | 🔒 Password Protected")
