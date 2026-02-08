from langchain_core.documents import Document
from pathlib import Path

def load_project_text(text: str):
    """Load text input as a LangChain Document."""
    return [Document(page_content=text)]

def load_readme_file(file_path: str):
    """Load README file as a LangChain Document."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return [Document(page_content=content, metadata={"source": file_path})]
