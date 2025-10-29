# Water.org Policy RAG System - Proof of Concept

A Retrieval-Augmented Generation (RAG) system for querying organizational policies and procedures using natural language.

## 🌟 Features

- **PDF Processing**: Automatically extracts and chunks policy documents
- **Semantic Search**: Uses vector embeddings to find relevant policies
- **Natural Language Interface**: Chat-based interface powered by Claude
- **Metadata Filtering**: Filter by department, region, or policy type
- **Source Citations**: Always shows which policies informed each answer
- **Easy Setup**: Local deployment with no external dependencies except API key

## 📋 Prerequisites

- Python 3.9 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- PDF policy documents

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this repository
# Navigate to the project directory

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API key
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Prepare Your Policy Documents

**Option A: Simple Setup** (All policies get same metadata)
```bash
# Create a policies directory
mkdir policies

# Copy your PDF files into it
cp /path/to/your/policies/*.pdf policies/
```

**Option B: With Metadata** (Recommended)
```bash
# Create a policies directory
mkdir policies

# Copy your PDF files
cp /path/to/your/policies/*.pdf policies/

# Create a metadata CSV file (see policies_metadata_template.csv for format)
# CSV should have: filename, department, region, policy_type, effective_date, description
```

### 4. Index Your Documents

**Simple ingestion:**
```bash
python ingest.py ./policies
```

**With metadata CSV:**
```bash
python ingest.py ./policies policies_metadata.csv
```

This will:
- Extract text from all PDFs
- Chunk the documents intelligently
- Generate embeddings
- Store everything in a local ChromaDB database

### 5. Launch the Chat Interface

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 💬 Using the Chat Interface

### First Time Setup
1. Enter your Anthropic API key in the sidebar
2. Click "Initialize System"
3. Your indexed policies will be loaded

### Asking Questions

Simply type questions like:
- "What is our expense reimbursement policy?"
- "How do I submit a travel request?"
- "What are the remote work guidelines?"
- "Can I expense meals during business travel?"

### Using Filters

Use the sidebar filters to narrow searches:
- **Department**: Finance, HR, Technology, etc.
- **Region**: Global, US, Kenya, India, etc.
- **Type**: Policy vs Procedure

### Viewing Sources

Each answer includes a "Sources" section showing which policies were used.

## 📁 Project Structure

```
policy-rag/
├── app.py                          # Streamlit chat interface
├── document_processor.py           # PDF extraction and chunking
├── vector_store.py                 # ChromaDB vector database manager
├── query_engine.py                 # RAG query logic with Claude
├── ingest.py                       # Bulk document ingestion script
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment variable template
├── policies_metadata_template.csv  # Example metadata format
├── README.md                       # This file
├── policies/                       # Your PDF documents (create this)
└── chroma_db/                      # Vector database (auto-created)
```

## 📊 Metadata CSV Format

Create a CSV file with the following columns:

```csv
filename,department,region,policy_type,effective_date,description
expense_policy.pdf,Finance,Global,Policy,2024-01-01,Employee expense reimbursement
travel_policy.pdf,Finance,Global,Policy,2024-01-01,Business travel guidelines
```

**Required columns:**
- `filename`: Name of the PDF file (must match actual filename)
- `department`: Department that owns the policy
- `region`: Geographic scope (e.g., Global, US, Kenya)
- `policy_type`: "Policy" or "Procedure"

**Optional columns:**
- `effective_date`: When policy took effect (YYYY-MM-DD)
- `description`: Brief description of the policy

## 🔧 Configuration

### Chunking Parameters

In `document_processor.py`, adjust:
```python
DocumentProcessor(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200     # Overlap between chunks
)
```

### Retrieval Settings

In `query_engine.py`, modify:
```python
query_engine.query(
    question=question,
    n_results=5,          # Number of chunks to retrieve
    temperature=0.3       # Claude creativity (0-1)
)
```

### Embedding Model

In `vector_store.py`, change the model:
```python
VectorStoreManager(
    embedding_model="all-MiniLM-L6-v2"  # Fast and good for most uses
    # Or: "all-mpnet-base-v2"            # More accurate but slower
)
```

## 🧪 Testing with Sample Policies

1. Create 3-5 sample policy PDFs covering different topics
2. Add them to the `policies/` directory
3. Run ingestion: `python ingest.py ./policies`
4. Launch the app: `streamlit run app.py`
5. Try these test questions:
   - Ask about specific policy topics
   - Try filtering by department
   - Ask questions that span multiple policies
   - Ask about something NOT in your policies (should say it doesn't know)

## 📈 Scaling Up

This POC is designed for ~40 policies. For production:

### Current Capacity
- ✅ 40 policies (~2000-4000 chunks)
- ✅ Local deployment
- ✅ Single user or team use

### To Scale Further
- **100+ policies**: Consider Pinecone or Weaviate instead of ChromaDB
- **Multiple users**: Deploy on cloud (AWS, Azure, GCP)
- **Authentication**: Add SSO integration
- **Analytics**: Track query patterns and feedback

## 🐛 Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not found"
Make sure `.env` file exists with your API key:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### "No documents indexed"
Run the ingestion script first:
```bash
python ingest.py ./policies
```

### PDFs not processing
- Ensure PDFs are text-based (not scanned images)
- Check file permissions
- Verify files are actually in the directory

### Poor answer quality
- Increase `n_results` to retrieve more chunks
- Adjust chunk_size and overlap in document_processor.py
- Verify your PDFs have good text extraction
- Add more context to your questions

## 💰 Cost Estimates

Based on typical usage:

**One-time Setup:**
- Document ingestion: ~$0.50 (for 40 policies)

**Ongoing Usage:**
- Per query: ~$0.01-0.03
- 100 queries/day: ~$30-90/month
- Embedding storage: Free (ChromaDB is local)

**API Rate Limits:**
- Check your Anthropic tier limits
- Default: ~50 queries/minute

## 🔐 Security Considerations

**For POC (Current):**
- API key in .env file (don't commit to git!)
- Local database (not accessible externally)
- No user authentication

**For Production:**
- Use secret management (AWS Secrets Manager, etc.)
- Implement proper authentication
- Add audit logging
- Review policies for sensitive information
- Consider data encryption at rest

## 📝 Next Steps

After validating the POC:

1. **Gather Feedback**
   - Deploy to 5-10 pilot users
   - Track which questions work well/poorly
   - Collect feature requests

2. **Improve Accuracy**
   - Fine-tune chunking based on policy structure
   - Add policy cross-references
   - Implement feedback mechanisms

3. **Add Features**
   - Email alerts for policy updates
   - Related policy suggestions
   - "I'm not sure" confidence scoring
   - Export answers to PDF

4. **Productionize**
   - Cloud deployment
   - User authentication
   - Usage analytics dashboard
   - Automated policy ingestion pipeline

## 🤝 Support

For questions or issues:
- Check the troubleshooting section
- Review code comments in Python files
- Test with a single policy first
- Verify API key is valid

## 📄 License

This is a proof-of-concept system for Water.org internal use.

---

**Built with:** Claude (Anthropic), ChromaDB, Streamlit, Sentence Transformers
