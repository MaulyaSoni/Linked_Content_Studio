def get_retriever(vectorstore, k=4):
    """Get retriever from vector store."""
    if vectorstore is None:
        return None
    return vectorstore.as_retriever(search_kwargs={"k": k})

def retrieve_context(vectorstore, query, k=3):
    """Retrieve context documents related to the query."""
    if vectorstore is None:
        return ""
    retriever = get_retriever(vectorstore, k=k)
    docs = retriever.invoke(query)
    return "\n".join([d.page_content for d in docs])
