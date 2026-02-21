"""
Document Processor Tool
=======================
Extracts text and key insights from PDFs, DOCX, and TXT files.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DocumentResult:
    """Result from document processing."""
    success: bool
    full_text: str = ""
    key_points: List[str] = field(default_factory=list)
    summary: str = ""
    title: str = ""
    word_count: int = 0
    content_type: str = ""
    error_message: str = ""


class DocumentProcessor:
    """
    Extracts text and insights from PDFs, DOCX, and TXT documents.
    
    Dependency note: PyPDF2 and python-docx are optional.
    Falls back gracefully if not installed.
    """

    SUPPORTED = {".pdf", ".docx", ".doc", ".txt", ".md"}

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ DocumentProcessor initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def process(self, file_path: str) -> DocumentResult:
        """Process a document and extract its content."""
        path = Path(file_path)
        if not path.exists():
            return DocumentResult(success=False, error_message=f"File not found: {file_path}")
        if path.suffix.lower() not in self.SUPPORTED:
            return DocumentResult(success=False, error_message=f"Unsupported: {path.suffix}")

        try:
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                text = self._extract_pdf(str(path))
            elif suffix in (".docx", ".doc"):
                text = self._extract_docx(str(path))
            else:  # .txt / .md
                text = path.read_text(encoding="utf-8", errors="ignore")

            if not text.strip():
                return DocumentResult(success=False, error_message="No text extracted from document")

            key_points = self._extract_key_points(text)
            summary = self._summarize(text)

            return DocumentResult(
                success=True,
                full_text=text,
                key_points=key_points,
                summary=summary,
                title=path.stem,
                word_count=len(text.split()),
                content_type=suffix.lstrip("."),
            )
        except Exception as exc:
            logger.error(f"❌ Document processing failed: {exc}")
            return DocumentResult(success=False, error_message=str(exc))

    # ------------------------------------------------------------------
    # EXTRACTORS
    # ------------------------------------------------------------------

    def _extract_pdf(self, path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            import PyPDF2  # type: ignore

            text_parts = []
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except ImportError:
            logger.warning("⚠️ PyPDF2 not installed. Install via: pip install PyPDF2")
            return f"[PDF content from {path} — install PyPDF2 to extract text]"
        except Exception as exc:
            logger.error(f"PDF extraction error: {exc}")
            return ""

    def _extract_docx(self, path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            import docx  # type: ignore

            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            logger.warning("⚠️ python-docx not installed. Install via: pip install python-docx")
            return f"[DOCX content from {path} — install python-docx to extract text]"
        except Exception as exc:
            logger.error(f"DOCX extraction error: {exc}")
            return ""

    # ------------------------------------------------------------------
    # LLM HELPERS
    # ------------------------------------------------------------------

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points via LLM or heuristic fallback."""
        if self.llm:
            try:
                truncated = text[:3000]
                result = self.llm.generate(
                    prompt=f"Extract the 5 most important key points from this text as a numbered list:\n\n{truncated}",
                    system_prompt="You are a professional content analyst.",
                )
                if result.success:
                    lines = [l.strip().lstrip("0123456789.-• ") for l in result.content.split("\n") if l.strip()]
                    return [l for l in lines if len(l) > 10][:7]
            except Exception:
                pass
        # Heuristic: first sentence of each paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
        points = []
        for para in paragraphs[:7]:
            first = para.split(".")[0].strip()
            if first:
                points.append(first)
        return points

    def _summarize(self, text: str) -> str:
        """Summarize document text."""
        if self.llm:
            try:
                truncated = text[:4000]
                result = self.llm.generate(
                    prompt=f"Summarize this document in 2-3 sentences for LinkedIn content creation:\n\n{truncated}",
                    system_prompt="Provide a concise, professional summary.",
                )
                if result.success:
                    return result.content.strip()
            except Exception:
                pass
        # Fallback: first 300 chars
        return text[:300].strip() + "..."
