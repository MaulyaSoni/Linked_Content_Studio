from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

def create_vector_store(docs):
    """Create FAISS vector store from documents using embeddings."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    
    # Try HuggingFace embeddings first, fallback to OpenAI if unavailable
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✅ Using HuggingFace embeddings")
    except ImportError:
        print("⚠️ sentence-transformers not installed, using OpenAI embeddings")
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    return FAISS.from_documents(chunks, embeddings)