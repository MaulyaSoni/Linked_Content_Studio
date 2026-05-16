import os
import re
import replicate
from typing import Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings


class ImageGenerationService:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    async def generate_for_post(
        self,
        post_content: str,
        style: str = "modern_professional",
    ) -> Dict:
        """
        Full pipeline: extract concept → build image prompt → call Replicate → return URL
        """
        try:
            # Step 1: extract visual concept
            concept = await self._extract_concept(post_content)

            # Step 2: build image prompt
            image_prompt = self._build_image_prompt(concept, style)

            # Step 3: call Replicate (SDXL)
            if not os.getenv("REPLICATE_API_TOKEN"):
                return {
                    "success": False,
                    "error": "REPLICATE_API_TOKEN missing",
                    "url": "https://via.placeholder.com/1200x628?text=Configure+Replicate+API"
                }

            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a60c3b36b4bab839c580fc724bccc63c521b302d402d3beed3f60303",
                input={
                    "prompt":            image_prompt,
                    "negative_prompt":   "text, watermark, logo, people's faces, blur, low quality",
                    "width":             1200,
                    "height":            628,
                    "num_inference_steps": 25,
                    "guidance_scale":    7.5,
                },
            )

            image_url = output[0] if output else None

            return {
                "success": True,
                "url":     image_url,
                "prompt":  image_prompt,
                "concept": concept
            }

        except Exception as e:
            return {
                "success": False,
                "error":   str(e),
                "url":     "https://via.placeholder.com/1200x628?text=Generation+Failed"
            }

    async def _extract_concept(self, text: str) -> str:
        """Extract a single visual metaphor from the post text."""
        prompt = f"""
        Analyze this LinkedIn post and describe ONE sharp visual scene or metaphor that represents it.
        Avoid clichés. Be specific. No text in the image.
        
        POST:
        {text}
        
        Return ONLY the scene description (max 20 words):
        """
        resp = await self.llm.ainvoke([
            SystemMessage(content="You are a visual director. Describe scenes clearly."),
            HumanMessage(content=prompt)
        ])
        return resp.content.strip()

    def _build_image_prompt(self, concept: str, style: str) -> str:
        """Turn concept into a detailed SDXL prompt."""
        styles = {
            "modern_professional": "High-end corporate photography, cinematic lighting, 8k resolution, professional color grading, clean composition, shallow depth of field.",
            "digital_art": "Modern flat illustration, vibrant colors, clean lines, tech-focused, minimalist aesthetic, vector style.",
            "dramatic": "High contrast, moody lighting, bold shadows, powerful composition, cinematic 35mm film look."
        }
        
        style_suffix = styles.get(style, styles["modern_professional"])
        return f"{concept}. {style_suffix} LinkedIn-optimized, professional, sleek, high quality."
