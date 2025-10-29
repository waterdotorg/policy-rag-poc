# Water.org Policy RAG - Project Overview

## What We Built

A complete proof-of-concept RAG (Retrieval-Augmented Generation) system that allows Water.org employees to ask natural language questions about organizational policies and receive accurate, cited answers.

## Key Components

### 1. Document Processing (`document_processor.py`)
- Extracts text from PDF policy documents
- Intelligently chunks documents (1000 chars with 200 char overlap)
- Preserves metadata (department, region, policy type, etc.)
- Handles batch processing of multiple documents

### 2. Vector Storage (`vector_store.py`)
- Uses ChromaDB for local vector storage (no external dependencies)
- Generates embeddings using sentence-transformers
- Supports semantic search across all policies
- Enables metadata filtering (by department, region, type)
- Persists data locally for fast subsequent loads

### 3. RAG Query Engine (`query_engine.py`)
- Retrieves relevant policy chunks based on user questions
- Sends context + question to Claude API
- Engineered prompts ensure citation and accuracy
- Returns answers with source attribution

### 4. Chat Interface (`app.py`)
- Clean, intuitive Streamlit web interface
- Chat-based interaction pattern
- Real-time filtering by metadata
- Shows source policies for every answer
- Conversation history within session

### 5. Utilities
- `ingest.py`: Bulk document ingestion script
- `test_system.py`: Comprehensive testing suite
- `policies_metadata_template.csv`: Example metadata format
- `.env.template`: API key configuration template

## Architecture Flow

```
User Question
    ↓
Streamlit Interface (app.py)
    ↓
Query Engine (query_engine.py)
    ↓
Vector Store Search (vector_store.py)
    ↓
Retrieve Top 5 Relevant Chunks
    ↓
Format Context + Question
    ↓
Claude API Call
    ↓
Generated Answer with Citations
    ↓
Display to User
```

## Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Vector DB**: ChromaDB (local, embedded)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Claude Sonnet 4 (Anthropic API)
- **PDF Processing**: pypdf
- **Dependencies**: All listed in requirements.txt

## Key Features

✅ **Natural Language Queries**: Ask questions in plain English
✅ **Semantic Search**: Finds relevant policies even with different wording  
✅ **Source Citations**: Every answer shows which policies were used
✅ **Metadata Filtering**: Filter by department, region, or policy type
✅ **Local Deployment**: Runs entirely on your machine (except API calls)
✅ **Easy Updates**: Add new policies by re-running ingestion
✅ **Conversation Memory**: Maintains context within a session
✅ **Smart Chunking**: Breaks documents at sentence boundaries

## Setup Summary

### Time Required
- Initial setup: 5 minutes
- Document ingestion: 1-2 minutes per 10 policies
- First query: Immediate

### Prerequisites
- Python 3.9+
- Anthropic API key
- PDF policy documents

### Quick Start
1. `pip install -r requirements.txt`
2. Add API key to `.env` file
3. `python ingest.py ./policies`
4. `streamlit run app.py`

## Customization Options

### Easy to Adjust
- Chunk size and overlap (document_processor.py)
- Number of results retrieved (query_engine.py)
- Embedding model (vector_store.py)
- UI appearance (app.py)
- Metadata schema (any fields you want)

### Prompt Engineering
The system prompt in `query_engine.py` can be customized to:
- Change tone (more formal/casual)
- Add specific instructions (always mention effective dates, etc.)
- Include disclaimers
- Customize citation format

## Cost Estimates

### Development/POC Phase
- Setup: $0 (local embedding model)
- Ingestion: ~$0.50 (40 policies)
- Testing: ~$5-10 (100 test queries)

### Production Usage (estimated)
- Per query: $0.01-0.03
- 100 queries/day: ~$30-90/month
- Storage: $0 (local ChromaDB)

## Limitations & Considerations

### Current POC Limitations
- Single user (no authentication)
- Local deployment only
- No audit logging
- No feedback mechanism
- API key stored in .env file

### For Production, Add
- User authentication (SSO integration)
- Usage analytics and monitoring
- Feedback collection system
- Cloud deployment
- Automated policy update pipeline
- Version control for policies
- More sophisticated retrieval (hybrid search, reranking)

## Success Metrics to Track

1. **Accuracy**: % of queries answered correctly
2. **Coverage**: % of queries that find relevant policies
3. **Usage**: Number of queries per day/user
4. **Satisfaction**: User feedback ratings
5. **Time Saved**: vs. manual policy searches

## Next Steps

### Phase 1: Validation (2-3 weeks)
- Deploy to 5-10 pilot users
- Collect feedback on accuracy and usefulness
- Track which policies are most queried
- Identify gaps or problem areas

### Phase 2: Refinement (3-4 weeks)
- Tune chunking based on actual policy structure
- Improve prompt based on user feedback
- Add policy cross-references
- Implement basic analytics

### Phase 3: Production (4-6 weeks)
- Cloud deployment (AWS/Azure/GCP)
- Add authentication
- Build admin interface
- Create policy update workflow
- Implement monitoring and alerts

## Files Included

1. **README.md** - Comprehensive documentation
2. **QUICKSTART.md** - 5-minute setup guide
3. **app.py** - Streamlit chat interface
4. **document_processor.py** - PDF processing
5. **vector_store.py** - Vector database management
6. **query_engine.py** - RAG query logic
7. **ingest.py** - Bulk ingestion script
8. **test_system.py** - Testing suite
9. **requirements.txt** - Python dependencies
10. **.env.template** - API key template
11. **policies_metadata_template.csv** - Metadata example
12. **.gitignore** - Git exclusions

## Support & Documentation

- Start with QUICKSTART.md for immediate setup
- Reference README.md for detailed documentation
- Run test_system.py to verify everything works
- Check code comments for implementation details

## Security Notes

### Current Security Posture
- API key in .env file (not committed to git)
- Local database (no network exposure)
- No user authentication
- No encryption at rest

### For Production
- Use secret management service
- Implement role-based access control
- Add audit logging
- Encrypt sensitive data
- Review policies for PII/sensitive content

## Conclusion

This POC provides a fully functional policy chatbot that you can test with real policies immediately. It's designed to be simple to set up and customize while demonstrating the core capabilities of a RAG system.

The architecture is deliberately kept simple and local for quick iteration, but is designed with clear pathways to production deployment when ready.

**Start testing with 3-5 policies, gather feedback, and iterate from there!**

---
Built for Water.org Technology Team | October 2025
