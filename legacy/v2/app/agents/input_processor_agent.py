"""
Input Processor Agent
=====================
First agent in the pipeline.
Processes multi-modal input (text, images, documents, URLs) and
extracts structured meaning to hand off to the Research Agent.
"""

import time
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import AgentResult, BaseAgent
from tools.document_processor import DocumentProcessor
from tools.vision_analyzer import VisionAnalyzer
from tools.web_scraper import WebScraper


class InputProcessorAgent(BaseAgent):
    """Processes all input modalities and extracts core themes/content."""

    def __init__(self, llm_provider=None):
        super().__init__("InputProcessor", llm_provider)
        self.vision = VisionAnalyzer(llm_provider)
        self.doc_processor = DocumentProcessor(llm_provider)
        self.web_scraper = WebScraper(llm_provider)

    # ------------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------------

    def run(self, input_data: Dict) -> AgentResult:
        """
        Process multi-modal input.

        input_data keys (all optional, at least one required):
            text          : str  - raw text / topic
            image_paths   : list - paths to image files
            document_paths: list - paths to PDFs / DOCX
            urls          : list - web URLs to scrape
        """
        start = time.time()
        self.logger.info("📥 InputProcessorAgent: processing input...")

        text = input_data.get("text", "")
        image_paths: List[str] = input_data.get("image_paths", [])
        doc_paths: List[str] = input_data.get("document_paths", [])
        urls: List[str] = input_data.get("urls", [])

        if not any([text, image_paths, doc_paths, urls]):
            return self._failure("No input provided", time.time() - start)

        extracted_pieces: List[str] = []
        content_types: List[str] = []
        themes: List[str] = []

        # 1. Direct text
        if text:
            extracted_pieces.append(f"[TEXT INPUT]\n{text}")
            content_types.append("text")

        # 2. Images
        for path in image_paths:
            result = self.vision.analyze_image(path)
            if result.success:
                extracted_pieces.append(
                    f"[IMAGE: {path}]\n"
                    f"Description: {result.description}\n"
                    f"Themes: {', '.join(result.key_themes)}\n"
                    f"Content angles: {', '.join(result.content_angles)}"
                )
                themes.extend(result.key_themes)
                content_types.append("image")

        # 3. Documents
        for path in doc_paths:
            result = self.doc_processor.process(path)
            if result.success:
                extracted_pieces.append(
                    f"[DOCUMENT: {path}]\n"
                    f"Summary: {result.summary}\n"
                    f"Key points:\n" + "\n".join(f"  - {p}" for p in result.key_points)
                )
                content_types.append("document")

        # 4. URLs
        for url in urls:
            result = self.web_scraper.scrape(url)
            if result.success:
                extracted_pieces.append(
                    f"[URL: {url}]\n"
                    f"Title: {result.title}\n"
                    f"Description: {result.description}\n"
                    f"Key points:\n" + "\n".join(f"  - {p}" for p in result.key_points)
                )
                content_types.append("url")

        combined = "\n\n".join(extracted_pieces)

        # Use LLM to synthesize themes if available
        if self.llm and combined:
            synthesis = self.think(
                prompt=(
                    f"From the following multi-modal content, extract:\n"
                    f"1. Core topic / main theme\n"
                    f"2. Key messages (up to 5)\n"
                    f"3. Target audience\n"
                    f"4. Best LinkedIn post angle\n\n"
                    f"Content:\n{combined[:3000]}"
                ),
                system_prompt="You are an expert content strategist.",
            )
        else:
            synthesis = combined[:500]

        output = {
            "combined_content": combined,
            "synthesis": synthesis,
            "content_types": list(set(content_types)),
            "raw_text": text,
            "image_count": len(image_paths),
            "doc_count": len(doc_paths),
            "url_count": len(urls),
            "themes": themes,
        }

        return self._success(
            output=output,
            summary=f"Processed {len(extracted_pieces)} input sources ({', '.join(set(content_types))})",
            context={"extracted_content": combined[:2000], "synthesis": synthesis},
            next_hint="ResearchAgent",
            time=time.time() - start,
        )
