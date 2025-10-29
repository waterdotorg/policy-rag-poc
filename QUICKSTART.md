# Quick Start Guide - 5 Minutes to First Query

## Prerequisites
- Python 3.9+ installed
- Anthropic API key
- 3-5 sample policy PDFs ready

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### 2. Configure API Key (30 seconds)
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# OR set environment variable
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Test the System (1 minute)
```bash
python test_system.py
```

You should see:
```
✅ Document Processor: PASSED
✅ Vector Store: PASSED  
✅ Query Engine: PASSED
```

### 4. Add Your Policies (1 minute)
```bash
# Create policies directory
mkdir policies

# Copy your PDFs
cp /path/to/your/policy1.pdf policies/
cp /path/to/your/policy2.pdf policies/
cp /path/to/your/policy3.pdf policies/
```

### 5. Index Documents (1 minute)
```bash
python ingest.py ./policies
```

You should see:
```
Found 3 PDF files in ./policies
Processed policy1.pdf: 15 chunks created
Processed policy2.pdf: 12 chunks created
Processed policy3.pdf: 18 chunks created
✅ Successfully indexed 45 chunks from 3 documents
```

### 6. Launch Chat Interface (30 seconds)
```bash
streamlit run app.py
```

Browser will open to `http://localhost:8501`

### 7. Start Asking Questions!
In the sidebar:
1. Paste your API key (if not in .env)
2. Click "Initialize System"

Then ask questions like:
- "What is our expense policy?"
- "How do I submit a travel request?"
- "What are the remote work guidelines?"

## Troubleshooting

**"No module named X"**
```bash
pip install -r requirements.txt
```

**"API key not found"**
- Check .env file exists and has correct format
- OR paste key directly in Streamlit sidebar

**"No documents indexed"**
```bash
# Run ingestion first
python ingest.py ./policies
```

**PDFs not processing**
- Ensure PDFs contain actual text (not scanned images)
- Check file permissions
- Try with a different PDF

## What's Next?

### For Better Metadata (Optional)
Create `policies_metadata.csv`:
```csv
filename,department,region,policy_type,effective_date,description
policy1.pdf,Finance,Global,Policy,2024-01-01,Expense reimbursement
policy2.pdf,HR,Global,Policy,2024-01-01,Remote work guidelines
```

Then run:
```bash
python ingest.py ./policies policies_metadata.csv
```

### For Production Use
See full README.md for:
- Scaling to 40+ policies
- Adding authentication
- Cloud deployment
- Advanced configuration

## Need Help?

1. Check README.md for detailed documentation
2. Run `python test_system.py` to verify setup
3. Review code comments in Python files
4. Start with 1-2 simple policies to test

---

**Total setup time: ~5 minutes**
**First query to answer: ~10 seconds**

Now go try it out! 🚀
