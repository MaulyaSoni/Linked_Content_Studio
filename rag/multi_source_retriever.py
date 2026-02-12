"""
Multi-Source Retrieval - Advanced RAG with Weighted Context
Retrieves context from multiple sources and weights them for optimal relevance.
"""

from typing import List, Dict, Tuple
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores import FAISS
# Try HuggingFace embeddings import with fallback
try:
    from langchain_huggingface.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    from langchain_openai import OpenAIEmbeddings
import numpy as np


class MultiSourceRetriever:
    """
    Advanced RAG retriever combining multiple context sources.
    
    Sources:
    1. README (primary - highest weight)
    2. Example posts / case studies
    3. GitHub issues (problem statements)
    4. Commit messages (evolution)
    5. Documentation files
    
    Each source contributes differently to the context.
    """
    
    # Default weights: higher = more important
    DEFAULT_WEIGHTS = {
        "readme": 0.50,
        "examples": 0.20,
        "issues": 0.15,
        "commits": 0.10,
        "docs": 0.05
    }
    
    def __init__(self, embeddings=None):
        """Initialize multi-source retriever."""
        if embeddings is None:
            if HUGGINGFACE_AVAILABLE:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={"device": "cpu"}
                )
            else:
                print("⚠️ sentence-transformers not available, using OpenAI embeddings")
                self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        else:
            self.embeddings = embeddings
        
        self.vectorstores = {}
        self.weights = self.DEFAULT_WEIGHTS.copy()
    
    def add_source(self, source_name: str, documents: List[Document], weight: float = None):
        """
        Add a document source to the retriever.
        
        Args:
            source_name: Identifier for source (readme, issues, commits, etc)
            documents: List of Document objects from this source
            weight: Importance weight (0-1). If None, uses default.
        """
        if weight is not None:
            self.weights[source_name] = weight
        
        try:
            vectorstore = FAISS.from_documents(
                documents,
                self.embeddings
            )
            self.vectorstores[source_name] = vectorstore
        except Exception as e:
            print(f"⚠️ Failed to create vectorstore for {source_name}: {str(e)}")
    
    def retrieve_weighted(self, query: str, k: int = 5) -> Tuple[List[Document], Dict]:
        """
        Retrieve documents from all sources and weight them.
        
        Returns: (documents, weights_used)
        """
        all_results = []
        weights_used = {}
        
        total_weight = sum(self.weights.values())
        
        # Retrieve from each source
        for source_name, vectorstore in self.vectorstores.items():
            weight = self.weights.get(source_name, 0.1) / total_weight
            weights_used[source_name] = weight
            
            try:
                docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)
                
                for doc, score in docs_with_scores:
                    # Adjust score by source weight
                    adjusted_score = score * weight
                    
                    # Add source metadata
                    doc.metadata["source_type"] = source_name
                    doc.metadata["weight"] = weight
                    doc.metadata["original_score"] = score
                    doc.metadata["adjusted_score"] = adjusted_score
                    
                    all_results.append((doc, adjusted_score))
            except Exception as e:
                print(f"⚠️ Retrieval failed for {source_name}: {str(e)}")
        
        # Sort by adjusted score and take top k
        all_results.sort(key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in all_results[:k]]
        
        return top_docs, weights_used
    
    def build_weighted_context(self, query: str, k: int = 5) -> str:
        """
        Build a context string with source attribution.
        
        Highlights sources so model knows what's verified vs inferred.
        """
        docs, weights = self.retrieve_weighted(query, k)
        
        context = "=== WEIGHTED CONTEXT ===\n\n"
        context += f"Query: {query}\n"
        context += f"Sources used: {', '.join(weights.keys())}\n"
        context += "---\n\n"
        
        grouped_by_source = {}
        for doc in docs:
            source = doc.metadata.get("source_type", "unknown")
            if source not in grouped_by_source:
                grouped_by_source[source] = []
            grouped_by_source[source].append(doc)
        
        # Present sources in priority order
        priority_order = ["readme", "examples", "issues", "commits", "docs"]
        
        for source in priority_order:
            if source in grouped_by_source:
                weight_pct = weights.get(source, 0) * 100
                context += f"## [{source.upper()}] ({weight_pct:.0f}% weight)\n"
                
                for doc in grouped_by_source[source]:
                    context += f"\n📄 {doc.metadata.get('type', 'Content')}:\n"
                    context += f"{doc.page_content}\n"
                    context += f"(Confidence: {doc.metadata.get('adjusted_score', 0):.2f})\n"
                    context += "---\n"
        
        return context
    
    def get_retrieval_report(self) -> Dict:
        """Get information about configured sources."""
        return {
            "sources": list(self.vectorstores.keys()),
            "weights": self.weights,
            "total_docs": sum(
                len(vs.docstore._dict) for vs in self.vectorstores.values()
            ) if hasattr(self.vectorstores.get(list(self.vectorstores.keys())[0] if self.vectorstores else None, {}), 'docstore') else 0,
            "status": "ready" if self.vectorstores else "no_sources"
        }


class EnhancedRAGPipeline:
    """
    Full RAG pipeline with multi-source retrieval and context weighting.
    """
    
    def __init__(self, embeddings=None):
        self.retriever = MultiSourceRetriever(embeddings)
    
    def load_github_content(self, documents: List[Document]):
        """
        Load GitHub repository content and categorize by source.
        """
        readme_docs = [d for d in documents if d.metadata.get("type") == "readme"]
        issue_docs = [d for d in documents if d.metadata.get("type") == "issue"]
        commit_docs = [d for d in documents if d.metadata.get("type") == "commit"]
        example_docs = [d for d in documents if d.metadata.get("type") == "example"]
        doc_docs = [d for d in documents if d.metadata.get("type") == "documentation"]
        
        # Add with appropriate weights
        if readme_docs:
            self.retriever.add_source("readme", readme_docs, weight=0.50)
        if example_docs:
            self.retriever.add_source("examples", example_docs, weight=0.20)
        if issue_docs:
            self.retriever.add_source("issues", issue_docs, weight=0.15)
        if commit_docs:
            self.retriever.add_source("commits", commit_docs, weight=0.10)
        if doc_docs:
            self.retriever.add_source("docs", doc_docs, weight=0.05)
    
    def retrieve_context(self, query: str, k: int = 5) -> Tuple[str, Dict]:
        """
        Retrieve weighted context for query.
        
        Returns: (context_string, metadata)
        """
        context = self.retriever.build_weighted_context(query, k)
        report = self.retriever.get_retrieval_report()
        
        return context, report
    
    def get_source_diversity_score(self, query_results: List[Document]) -> float:
        """
        Calculate how diverse the retrieved context is across sources.
        
        Higher score = better diversity (not over-relying on one source)
        """
        source_counts = {}
        for doc in query_results:
            source = doc.metadata.get("source_type", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if not source_counts:
            return 0.0
        
        # Calculate entropy (diversity metric)
        total = sum(source_counts.values())
        entropy = 0.0
        for count in source_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        # Normalize to 0-1 (max entropy for n sources = log2(n))
        max_entropy = np.log2(len(source_counts))
        diversity_score = entropy / max_entropy if max_entropy > 0 else 0
        
        return diversity_score


# Global instance
_rag_pipeline = None


def get_enhancement_rag_pipeline(embeddings=None) -> EnhancedRAGPipeline:
    """Get or create enhanced RAG pipeline."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = EnhancedRAGPipeline(embeddings)
    return _rag_pipeline
