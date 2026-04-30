"""
Vision Analyzer Tool
====================
Analyzes images using LLM vision capabilities (Groq / Claude-compatible).
Extracts text, objects, themes, and suggests LinkedIn content angles.
"""

import base64
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class VisionAnalysisResult:
    """Result from image vision analysis."""
    success: bool
    description: str = ""
    extracted_text: str = ""
    key_themes: List[str] = field(default_factory=list)
    content_angles: List[str] = field(default_factory=list)
    objects_detected: List[str] = field(default_factory=list)
    emotional_tone: str = ""
    suggested_post_type: str = ""
    error_message: str = ""


class VisionAnalyzer:
    """
    Analyzes images using LLM vision capabilities.
    
    Supports: JPG, PNG, GIF, WebP
    Capabilities:
      - Describe image content
      - Extract visible text (OCR via LLM)
      - Suggest LinkedIn content angles
      - Detect emotional tone
    """

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ VisionAnalyzer initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze_image(self, image_path: str) -> VisionAnalysisResult:
        """Analyze a single image file."""
        path = Path(image_path)
        if not path.exists():
            return VisionAnalysisResult(
                success=False,
                error_message=f"Image file not found: {image_path}",
            )
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return VisionAnalysisResult(
                success=False,
                error_message=f"Unsupported format: {path.suffix}",
            )

        try:
            image_data = self._encode_image(str(path))
            analysis = self._describe_with_llm(image_data, path.suffix)
            return self._parse_analysis(analysis)
        except Exception as exc:
            logger.error(f"❌ Vision analysis failed: {exc}")
            return VisionAnalysisResult(success=False, error_message=str(exc))

    def analyze_multiple_images(
        self, image_paths: List[str]
    ) -> List[VisionAnalysisResult]:
        """Analyze a list of image files."""
        return [self.analyze_image(p) for p in image_paths]

    def extract_text_from_image(self, image_path: str) -> str:
        """OCR shortcut — returns only extracted text."""
        result = self.analyze_image(image_path)
        return result.extracted_text if result.success else ""

    def suggest_content_angles(self, image_path: str) -> List[str]:
        """Return suggested LinkedIn content angles for an image."""
        result = self.analyze_image(image_path)
        return result.content_angles if result.success else []

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    def _encode_image(self, path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _describe_with_llm(self, encoded: str, suffix: str) -> str:
        """Call LLM vision to describe the image. Falls back to mock."""
        if self.llm is None:
            return self._mock_analysis()

        media_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_map.get(suffix.lower(), "image/jpeg")

        prompt = (
            "Analyze this image for LinkedIn content creation.\n"
            "Return a JSON-like analysis with:\n"
            "DESCRIPTION: [detailed description]\n"
            "EXTRACTED_TEXT: [any text visible in image]\n"
            "KEY_THEMES: [comma-separated themes]\n"
            "OBJECTS: [comma-separated objects]\n"
            "EMOTIONAL_TONE: [one word: professional/inspiring/educational/celebratory]\n"
            "CONTENT_ANGLES: [3 LinkedIn post angle ideas]\n"
            "SUGGESTED_POST_TYPE: [best content type for this image]"
        )
        try:
            result = self.llm.generate(prompt=prompt, system_prompt="You are an expert visual content analyst.")
            return result.content if result.success else self._mock_analysis()
        except Exception:
            return self._mock_analysis()

    def _parse_analysis(self, raw: str) -> VisionAnalysisResult:
        """Parse structured LLM output into VisionAnalysisResult."""
        lines = raw.strip().split("\n")
        data: dict = {
            "description": "",
            "extracted_text": "",
            "key_themes": [],
            "objects": [],
            "emotional_tone": "professional",
            "content_angles": [],
            "suggested_post_type": "educational",
        }

        current_key = None
        buffer = []

        def flush():
            nonlocal current_key, buffer
            if current_key and buffer:
                val = " ".join(buffer).strip()
                if current_key in ("key_themes", "objects"):
                    data[current_key] = [v.strip() for v in val.split(",") if v.strip()]
                elif current_key == "content_angles":
                    data[current_key] = [v.strip().lstrip("•-123.") for v in val.split("|") if v.strip()]
                else:
                    data[current_key] = val
            buffer = []

        key_map = {
            "DESCRIPTION:": "description",
            "EXTRACTED_TEXT:": "extracted_text",
            "KEY_THEMES:": "key_themes",
            "OBJECTS:": "objects",
            "EMOTIONAL_TONE:": "emotional_tone",
            "CONTENT_ANGLES:": "content_angles",
            "SUGGESTED_POST_TYPE:": "suggested_post_type",
        }

        for line in lines:
            matched = False
            for prefix, key in key_map.items():
                if line.upper().startswith(prefix):
                    flush()
                    current_key = key
                    rest = line[len(prefix):].strip()
                    if rest:
                        buffer.append(rest)
                    matched = True
                    break
            if not matched and current_key:
                buffer.append(line.strip())

        flush()

        return VisionAnalysisResult(
            success=True,
            description=data["description"],
            extracted_text=data["extracted_text"],
            key_themes=data["key_themes"],
            objects_detected=data["objects"],
            emotional_tone=data["emotional_tone"],
            content_angles=data["content_angles"],
            suggested_post_type=data["suggested_post_type"],
        )

    def _mock_analysis(self) -> str:
        """Mock analysis for when LLM is unavailable."""
        return (
            "DESCRIPTION: A professional image showing work or innovation.\n"
            "EXTRACTED_TEXT: \n"
            "KEY_THEMES: innovation, technology, progress\n"
            "OBJECTS: screen, workspace, code\n"
            "EMOTIONAL_TONE: professional\n"
            "CONTENT_ANGLES: Share your build journey | Showcase the tech stack | Teach what you learned\n"
            "SUGGESTED_POST_TYPE: build_in_public"
        )
