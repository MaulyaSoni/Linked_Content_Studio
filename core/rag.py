"""
RAG Engine - Simplified Embedding + Retrieval
===========================================
Clean RAG implementation that replaces complex retrieval chains.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .models import PostRequest, RepoContext, RAGContext
from langchain_core.documents import Document



class RAGEngine:
    """
    Simplified RAG engine for LinkedIn content generation.
    
    Handles:
    - Document loading and chunking
    - Vector embeddings with fallback
    - Context retrieval and ranking
    - Quality assessment
    
    Production Optimizations:
    - Singleton pattern for embedding model (loads once)
    - Lazy initialization
    - Memory efficient
    """
    
    # Singleton embedding model - loads once, shared across instances
    _embedding_model = None
    _embedding_lock = False
    
    def __init__(self):
        """Initialize RAG engine with singleton embedding provider."""
        self.logger = logging.getLogger(__name__)
        self.embeddings = self._init_embeddings()
        self.vector_store = None
        
    def _init_embeddings(self):
        """Initialize embeddings with singleton pattern for production efficiency."""
        
        # Use singleton if already loaded
        if RAGEngine._embedding_model is not None:
            self.logger.info("✅ Using cached embedding model")
            return RAGEngine._embedding_model
        
        # Prevent concurrent initialization
        if RAGEngine._embedding_lock:
            self.logger.info("⏳ Waiting for embedding model to load...")
            import time
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if RAGEngine._embedding_model is not None:
                    return RAGEngine._embedding_model
        
        # Mark as loading
        RAGEngine._embedding_lock = True
        
        try:
            # Try HuggingFace embeddings first (free)
            from langchain_huggingface import HuggingFaceEmbeddings
            
            self.logger.info("🔄 Loading embedding model (first time only)...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            
            # Cache for future use
            RAGEngine._embedding_model = embeddings
            self.logger.info("✅ Embedding model loaded and cached")
            return embeddings
            
        except ImportError:
            self.logger.warning("sentence-transformers not available, trying OpenAI embeddings")
            
            # Fallback to OpenAI embeddings
            try:
                import os
                if os.getenv("OPENAI_API_KEY"):
                    from langchain_openai import OpenAIEmbeddings
                    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
                    RAGEngine._embedding_model = embeddings
                    self.logger.info("✅ OpenAI embeddings loaded and cached")
                    return embeddings
                else:
                    self.logger.warning("No OPENAI_API_KEY found")
            except ImportError:
                self.logger.warning("OpenAI embeddings not available")
            
            # No embeddings available - will use simple text matching
            self.logger.warning("⚠️ No embeddings available - using simple text matching")
            return None
            
        finally:
            RAGEngine._embedding_lock = False
    
    def retrieve_context(self, request: PostRequest) -> RAGContext:
        """
        Main retrieval method - gets context for generation.
        
        Args:
            request: PostRequest with GitHub URL or text input
            
        Returns:
            RAGContext with retrieved information
        """
        
        if request.github_url:
            return self._retrieve_github_context(request.github_url)
        elif request.text_input:
            return self._retrieve_text_context(request.text_input, request.topic)
        else:
            return self._retrieve_topic_context(request.topic)
    
    def _retrieve_github_context(self, github_url: str) -> RAGContext:
        """Retrieve and process GitHub repository context with production-safe fallbacks."""
        
        try:
            # Use simplified GitHub loader
            from loaders.github_loader import GitHubLoader
            loader = GitHubLoader()
            
            # Get repository context with fallback strategy (never crashes)
            repo_context = loader.load_with_fallback(github_url)
            
            # Build consolidated context
            context_parts = []
            sources_used = []
            
            if repo_context.readme_content:
                context_parts.append(f"README:\n{repo_context.readme_content[:2000]}")
                sources_used.append("readme")
            
            if repo_context.description:
                context_parts.append(f"DESCRIPTION: {repo_context.description}")
                sources_used.append("metadata")
            
            if repo_context.file_structure:
                structure = "\n".join(repo_context.file_structure[:20])  # Top 20 files
                context_parts.append(f"FILE STRUCTURE:\n{structure}")
                sources_used.append("file_structure")
            
            if repo_context.recent_commits:
                commits = "\n".join(repo_context.recent_commits[:5])  # Recent 5 commits
                context_parts.append(f"RECENT COMMITS:\n{commits}")  
                sources_used.append("commits")
            
            if repo_context.dependencies:
                deps = ", ".join(repo_context.dependencies[:10])  # Top 10 dependencies
                context_parts.append(f"TECH STACK: {deps}")
                sources_used.append("dependencies")
            
            consolidated_context = "\n\n".join(context_parts)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(repo_context)
            
            return RAGContext(
                content=consolidated_context,
                sources_used=sources_used,
                quality_score=quality_score,
                repo_context=repo_context
            )
            
        except Exception as e:
            self.logger.error(f"GitHub context retrieval failed: {e}")
            
            # Fallback: basic context from URL
            repo_name = github_url.split('/')[-1].replace('.git', '')
            return RAGContext(
                content=f"GitHub repository: {repo_name}\nAnalyzing repository structure and codebase.",
                sources_used=["github_url"],
                quality_score=0.3  # Low quality fallback
            )
    
    def _retrieve_text_context(self, text_input: str, topic: str) -> RAGContext:
        """Retrieve context from provided text input."""
        
        # For text input, we can enhance with topic-related context
        enhanced_context = f"TOPIC: {topic}\n\nCONTENT:\n{text_input}"
        
        # Simple quality assessment based on text length and structure
        quality_score = min(1.0, len(text_input) / 1000)  # Better with more content
        if topic:
            quality_score = min(1.0, quality_score + 0.2)  # Bonus for having topic
        
        return RAGContext(
            content=enhanced_context,
            sources_used=["text_input", "topic"] if topic else ["text_input"],
            quality_score=quality_score
        )
    
    def _retrieve_topic_context(self, topic: str) -> RAGContext:
        """Retrieve context for topic-only generation."""
        
        # For topic-only, create structured context
        context = f"""
        TOPIC: {topic}
        
        Context: Generate a LinkedIn post about {topic} that:
        - Provides valuable insights
        - Engages the professional audience  
        - Demonstrates expertise
        - Encourages discussion
        """
        
        return RAGContext(
            content=context,
            sources_used=["topic"],
            quality_score=0.6  # Medium quality - topic only
        )
    
    def _calculate_quality_score(self, repo_context: RepoContext) -> float:
        """Calculate context quality score (0-1 scale)."""
        
        score = 0.0
        
        # README availability (most important)
        if repo_context.readme_content:
            readme_length = len(repo_context.readme_content)
            if readme_length > 2000:
                score += 0.4  # Excellent README
            elif readme_length > 500:
                score += 0.3  # Good README  
            else:
                score += 0.2  # Basic README
        
        # Repository metadata
        if repo_context.description:
            score += 0.1
        if repo_context.topics:
            score += 0.1
        if repo_context.stars > 10:
            score += 0.1
        
        # File structure and dependencies
        if repo_context.file_structure:
            score += 0.1
        if repo_context.dependencies:
            score += 0.1
        
        # Recent activity
        if repo_context.recent_commits:
            score += 0.1
        
        return min(1.0, score)
    
    def create_vector_store(self, documents: List[Document]):
        """Create vector store from documents (if embeddings available)."""
        
        if not self.embeddings:
            self.logger.warning("No embeddings available - skipping vector store creation")
            return None
        
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            
            # Chunk documents
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100
            )
            chunks = splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            self.logger.info(f"Created vector store with {len(chunks)} chunks")
            
            return self.vector_store
            
        except Exception as e:
            self.logger.error(f"Vector store creation failed: {e}")
            return None
    
    def semantic_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform semantic search if vector store available."""
        
        if not self.vector_store:
            self.logger.warning("No vector store available for semantic search")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []
    
    def get_status(self) -> Dict[str, any]:
        """Get RAG engine status."""
        return {
            "embeddings_available": bool(self.embeddings),
            "vector_store_ready": bool(self.vector_store),
            "embedding_model": (
                self.embeddings.model_name if hasattr(self.embeddings, 'model_name') 
                else str(type(self.embeddings).__name__)
            ) if self.embeddings else "none"
        }


class SimpleTextMatcher:
    """
    Fallback text matching when embeddings are unavailable.
    Uses keyword matching and basic scoring.
    """
    
    @staticmethod
    def find_relevant_content(query: str, documents: List[str]) -> List[Tuple[str, float]]:
        """Find relevant content using simple text matching."""
        
        query_words = set(query.lower().split())
        results = []
        
        for doc in documents:
            doc_words = set(doc.lower().split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(doc_words))
            total_words = len(query_words.union(doc_words))
            
            if total_words > 0:
                score = overlap / total_words
                if score > 0.1:  # Minimum relevance threshold
                    results.append((doc, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:5]  # Top 5 matches


# Factory function
def create_rag_engine() -> RAGEngine:
    """Factory function to create RAG engine.""" 
    return RAGEngine()


if __name__ == "__main__":
    # Quick test
    rag = create_rag_engine()
    print(f"RAG Engine Status: {rag.get_status()}")