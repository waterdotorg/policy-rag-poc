# Deployment Checklist

Use this checklist to get your Policy RAG system up and running.

## ☐ Pre-Deployment

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] Git installed (optional, for version control)
- [ ] Text editor or IDE ready
- [ ] Terminal/command prompt access

### Get API Key
- [ ] Go to https://console.anthropic.com/
- [ ] Create account or log in
- [ ] Generate API key
- [ ] Save key securely

### Prepare Policies
- [ ] Identify 3-5 policies for initial testing
- [ ] Ensure PDFs are text-based (not scanned images)
- [ ] Note metadata: department, region, type for each
- [ ] (Optional) Create metadata CSV file

## ☐ Installation

### Download & Extract
- [ ] Download the policy-rag-poc folder
- [ ] Extract to your preferred location
- [ ] Open terminal in project directory

### Install Dependencies
```bash
pip install -r requirements.txt
```
- [ ] Installation completed without errors
- [ ] Note: First run downloads ~100MB of models

### Configure API Key
Choose ONE method:

**Option A: .env file (recommended)**
```bash
cp .env.template .env
# Edit .env and add your key
```
- [ ] .env file created
- [ ] API key added

**Option B: Environment variable**
```bash
export ANTHROPIC_API_KEY=your_key_here
```
- [ ] Environment variable set

## ☐ Testing

### Run System Tests
```bash
python test_system.py
```

Expected results:
- [ ] ✅ Document Processor: PASSED
- [ ] ✅ Vector Store: PASSED
- [ ] ✅ Query Engine: PASSED

If any test fails:
- [ ] Check error message
- [ ] Verify API key is correct
- [ ] Ensure all dependencies installed
- [ ] Try running individual components

## ☐ Document Ingestion

### Prepare Directory
```bash
mkdir policies
```
- [ ] policies/ directory created
- [ ] PDF files copied to policies/

### Create Metadata (Optional but Recommended)
```bash
cp policies_metadata_template.csv policies_metadata.csv
# Edit CSV with your policy information
```
- [ ] Metadata CSV created
- [ ] All filenames match actual PDFs
- [ ] Metadata fields completed

### Run Ingestion
**Without metadata:**
```bash
python ingest.py ./policies
```

**With metadata:**
```bash
python ingest.py ./policies policies_metadata.csv
```

Expected output:
- [ ] Found X PDF files
- [ ] Processed each file (N chunks created)
- [ ] ✅ Successfully indexed total chunks
- [ ] No error messages

## ☐ Launch Application

### Start Streamlit
```bash
streamlit run app.py
```

- [ ] Browser opens to http://localhost:8501
- [ ] No error messages in terminal
- [ ] Interface loads completely

### Initial Setup in UI
- [ ] Enter API key in sidebar (if not in .env)
- [ ] Click "Initialize System"
- [ ] System initializes successfully
- [ ] Document count shows in sidebar

## ☐ Testing Queries

### Basic Functionality
Test with these types of questions:

Simple factual query:
- [ ] "What is our [specific policy name]?"
- [ ] Answer returned with source citation

Search across policies:
- [ ] "How do I [perform some action]?"
- [ ] Multiple sources shown if relevant

Test uncertainty:
- [ ] Ask about something NOT in your policies
- [ ] System says it doesn't have that information

### Filter Testing
- [ ] Apply department filter
- [ ] Search with filter active
- [ ] Results only from that department

### Conversation Flow
- [ ] Ask a question
- [ ] Ask a follow-up question
- [ ] Conversation history maintained

## ☐ Quality Validation

### Accuracy Check
For 5-10 test questions:
- [ ] Answers are factually correct
- [ ] Sources are properly cited
- [ ] No hallucinated information
- [ ] Answers are relevant and helpful

### Edge Cases
- [ ] Vague questions get clarifying responses
- [ ] Out-of-scope questions handled gracefully
- [ ] Complex questions retrieve multiple sources
- [ ] Policy names are recognized

## ☐ Documentation

### Team Documentation
- [ ] Document where policies are stored
- [ ] Write instructions for adding new policies
- [ ] Create FAQ for common questions
- [ ] Note any policy-specific quirks

### Gather Initial Feedback
- [ ] Share with 2-3 test users
- [ ] Collect initial reactions
- [ ] Note questions that work well
- [ ] Note questions that don't work well

## ☐ Maintenance Setup

### Regular Tasks
- [ ] Plan for monthly policy updates
- [ ] Define who manages the system
- [ ] Set up backup of chroma_db/ folder
- [ ] Plan for monitoring usage

### Future Enhancements
- [ ] List desired features
- [ ] Prioritize improvements
- [ ] Set timeline for next phase

## ☐ Troubleshooting Reference

Keep handy:
- [ ] README.md for detailed docs
- [ ] QUICKSTART.md for quick reference
- [ ] test_system.py for diagnostics
- [ ] Your API key (securely stored)

### Common Issues

**"Module not found"**
- Solution: pip install -r requirements.txt

**"API key not found"**
- Solution: Check .env file or paste key in UI

**"No documents indexed"**
- Solution: Run python ingest.py ./policies

**Poor answer quality**
- Check: Are PDFs text-extractable?
- Check: Are questions specific enough?
- Try: Increasing n_results in query

**Slow responses**
- Normal: First query initializes model (~5 seconds)
- Normal: Claude API calls take 2-5 seconds
- Issue: If >10 seconds, check internet connection

## Success Criteria

You're ready to go when:
- [x] All tests pass
- [x] Documents are indexed
- [x] Can ask questions and get answers
- [x] Sources are cited correctly
- [x] Test users can access and use system

## Next Steps After Deployment

1. **Week 1-2: Pilot Testing**
   - Deploy to 5-10 users
   - Collect feedback daily
   - Fix any immediate issues

2. **Week 3-4: Refinement**
   - Analyze usage patterns
   - Tune retrieval parameters
   - Add missing policies

3. **Month 2: Expansion**
   - Add all 40 policies
   - Expand user base
   - Plan production deployment

## Questions or Issues?

- Check PROJECT_OVERVIEW.md for architecture details
- Review README.md for comprehensive documentation
- Run test_system.py to diagnose issues
- Check code comments for implementation details

---

**Estimated Time to Complete Checklist: 30-60 minutes**

Good luck with your deployment! 🚀
