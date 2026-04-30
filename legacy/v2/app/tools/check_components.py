import traceback

print('--- Component checks ---')

# Embeddings
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print('EMBEDDINGS: import OK')
    try:
        e = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        print('EMBEDDINGS: init OK')
    except Exception as ex:
        print('EMBEDDINGS: init ERROR ->', repr(ex))
except Exception as ex:
    print('EMBEDDINGS: import ERROR ->', repr(ex))

# Chroma / vectorstore
try:
    from langchain_community.vectorstores import Chroma
    print('CHROMADB: import OK')
except Exception as ex:
    print('CHROMADB: import ERROR ->', repr(ex))

# GitHub loader
try:
    from loaders.github import GitHubLoader
    loader = GitHubLoader()
    print('GITHUB_LOADER: init OK')
    try:
        content = loader.load('https://github.com/MaulyaSoni/AIrbnb-clone')
        print('GITHUB_LOADER: load OK -> length:', len(content) if content else 0)
    except Exception as ex:
        print('GITHUB_LOADER: load ERROR ->', repr(ex))
except Exception as ex:
    print('GITHUB_LOADER: init ERROR ->', repr(ex))

# RAGEngine init
try:
    from core.rag import RAGEngine
    print('RAG: import OK')
    try:
        r = RAGEngine()
        print('RAG: init OK')
    except Exception as ex:
        print('RAG: init ERROR ->', repr(ex))
except Exception as ex:
    print('RAG: import ERROR ->', repr(ex))

print('--- End checks ---')
