"""
RAG Query Engine for Policy RAG System
Handles question answering using Claude API with retrieved context
"""

import os
from typing import List, Dict, Any, Optional
from anthropic import Anthropic


class RAGQueryEngine:
    """Query engine that combines retrieval with Claude for answering questions"""
    
    def __init__(self, vector_store, api_key: Optional[str] = None):
        """
        Initialize query engine
        
        Args:
            vector_store: VectorStoreManager instance
            api_key: Anthropic API key (if not provided, reads from ANTHROPIC_API_KEY env var)
        """
        self.vector_store = vector_store
        
        # Initialize Anthropic client
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set as environment variable")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def format_context(self, search_results: Dict[str, Any]) -> str:
        """
        Format search results into context string
        
        Args:
            search_results: Results from vector store search
            
        Returns:
            Formatted context string
        """
        documents = search_results.get('documents', [[]])[0]
        metadatas = search_results.get('metadatas', [[]])[0]
        
        if not documents:
            return "No relevant policy documents found."
        
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(documents, metadatas), 1):
            source = metadata.get('filename', 'Unknown')
            dept = metadata.get('department', 'Unknown')
            region = metadata.get('region', 'Unknown')
            policy_type = metadata.get('policy_type', 'Unknown')
            
            context_parts.append(
                f"[Document {i}]\n"
                f"Source: {source}\n"
                f"Department: {dept} | Region: {region} | Type: {policy_type}\n"
                f"Content: {doc}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def build_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for Claude
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a policy assistant for Water.org, a global non-profit organization. Your role is to help employees find and understand organizational policies and procedures.

IMPORTANT INSTRUCTIONS:
1. Answer questions based ONLY on the policy documents provided in the context below
2. Always cite the specific policy document (filename) when providing information
3. If the answer is not in the provided context, clearly state that you don't have that information in the available policies
4. If multiple policies are relevant, mention all of them
5. Be precise and helpful - provide the specific policy guidance, not just general information
6. If a policy seems unclear or ambiguous, acknowledge this and suggest the user may need to consult with their department or HR
7. Use a professional but friendly tone

CONTEXT FROM POLICY DOCUMENTS:
{context}

USER QUESTION:
{query}

Please provide a helpful answer based on the policy documents above. Remember to cite specific policies."""

        return prompt
    
    def query(
        self, 
        question: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            n_results: Number of documents to retrieve
            filter_metadata: Optional metadata filters
            temperature: Claude temperature setting (0-1, lower is more focused)
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Retrieve relevant documents
        search_results = self.vector_store.search(
            query=question,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        # Format context
        context = self.format_context(search_results)
        
        # Build prompt
        prompt = self.build_prompt(question, context)
        
        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = message.content[0].text
            
        except Exception as e:
            answer = f"Error generating response: {str(e)}"
        
        # Extract sources
        sources = []
        metadatas = search_results.get('metadatas', [[]])[0]
        for metadata in metadatas:
            source_info = {
                "filename": metadata.get('filename', 'Unknown'),
                "department": metadata.get('department', 'Unknown'),
                "region": metadata.get('region', 'Unknown'),
                "policy_type": metadata.get('policy_type', 'Unknown')
            }
            if source_info not in sources:
                sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "num_sources_retrieved": len(search_results.get('documents', [[]])[0])
        }
    
    def query_with_conversation_history(
        self,
        question: str,
        conversation_history: List[Dict[str, str]],
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question with conversation context
        
        Args:
            question: User's current question
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            n_results: Number of documents to retrieve
            filter_metadata: Optional metadata filters
            
        Returns:
            Dictionary with answer and sources
        """
        # For now, we'll use the simple query method
        # In a more advanced version, we could use conversation history to refine the search
        return self.query(question, n_results, filter_metadata)


# Example usage and testing
if __name__ == "__main__":
    from vector_store import VectorStoreManager
    
    # This is just for testing the structure
    # In practice, you'd initialize with actual vector store and API key
    
    print("RAG Query Engine module loaded successfully")
    print("To use: Initialize with vector_store and provide ANTHROPIC_API_KEY")
