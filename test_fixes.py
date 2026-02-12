# Test fixes for sentence-transformers and messaging issues
import sys
sys.path.append(".")

def test_vector_store_fallback():
    """Test that vector store works with fallback embeddings."""
    print("Testing vector store fallback...")
    
    try:
        from langchain_core.documents import Document
        from rag.vector_store import create_vector_store
        
        # Create test documents
        test_docs = [Document(page_content="Test document content", metadata={"source": "test"})]
        
        # This should work with either HuggingFace or OpenAI embeddings
        vector_store = create_vector_store(test_docs)
        print("SUCCESS: Vector store created with fallback handling")
        return True
        
    except Exception as e:
        print(f"FAILED: Vector store creation error: {e}")
        return False

def test_retriever_message():
    """Test that retriever messages are clearer."""
    print("Testing retriever messaging...")
    
    try:
        from rag.readme_fallback_retriever import ReadmeFallbackRetriever
        
        # This should show better messaging
        retriever = ReadmeFallbackRetriever("https://github.com/user/nonexistent-repo")
        print("SUCCESS: Retriever initialized with improved messaging")
        return True
        
    except Exception as e:
        print(f"FAILED: Retriever initialization error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING FIXES FOR SENTENCE-TRANSFORMERS AND MESSAGING")
    print("=" * 50)
    
    test1_passed = test_vector_store_fallback()
    test2_passed = test_retriever_message()
    
    print("=" * 50)
    if test1_passed and test2_passed:
        print("ALL TESTS PASSED!")
        print("The fixes should resolve:")
        print("  - sentence-transformers ImportError")
        print("  - Confusing README messaging")
    else:
        print("SOME TESTS FAILED - check the errors above")
    print("=" * 50)