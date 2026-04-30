try:
    import replicate
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False
    
from typing import Optional
from pydantic import BaseModel
from app.services.llm_service import LLMService
from app.core.config import settings


class ImageResult(BaseModel):
    """Result of image generation."""
    url: str
    prompt: str
    concept: str
    style: str


class ImageGenerationService:
    """Generate images for LinkedIn posts using Replicate API."""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def generate_image_for_post(
        self,
        post_text: str,
        style: str = "modern",
        brand_colors: Optional[dict] = None
    ) -> ImageResult:
        """Extract key visual concepts from post and generate image."""
        
        # Step 1: Extract visual concept from post
        concept = await self._extract_visual_concept(post_text)
        
        # Step 2: Create image prompt
        image_prompt = await self._create_image_prompt(concept, post_text, style)
        
        # Step 3: Generate image using Stable Diffusion via Replicate
        if settings.REPLICATE_API_TOKEN:
            image_url = await self._call_replicate(image_prompt)
        else:
            # Fallback: return placeholder
            image_url = "https://via.placeholder.com/1200x628"
        
        return ImageResult(
            url=image_url,
            prompt=image_prompt,
            concept=concept,
            style=style,
        )
    
    async def _extract_visual_concept(self, post_text: str) -> str:
        """Use LLM to extract key visual elements from post."""
        
        prompt = f"""
        Extract the main visual concept or scene that would best accompany this LinkedIn post.
        Be specific and visual.
        
        Post:
        {post_text}
        
        Return ONE sentence describing the visual concept:
        """
        
        response = await self.llm_service.generate(prompt)
        return response.content.strip()
    
    async def _create_image_prompt(
        self,
        concept: str,
        post_text: str,
        style: str
    ) -> str:
        """Create a detailed image prompt for Stable Diffusion."""
        
        style_descriptions = {
            "modern": "sleek, contemporary, professional, minimal",
            "vibrant": "colorful, energetic, dynamic, playful",
            "professional": "corporate, formal, business, polished",
            "creative": "artistic, imaginative, inspiring, unique",
        }
        
        style_desc = style_descriptions.get(style, "professional")
        
        # Extract theme from post
        if any(word in post_text.lower() for word in ["growth", "scale", "success"]):
            theme = "upward growth, success"
        elif any(word in post_text.lower() for word in ["team", "collaborate", "together"]):
            theme = "teamwork, collaboration"
        elif any(word in post_text.lower() for word in ["learn", "education", "knowledge"]):
            theme = "learning, knowledge, innovation"
        else:
            theme = "professional achievement"
        
        prompt = f"""
        Create a {style_desc} LinkedIn-optimized image for this concept:
        
        {concept}
        
        Theme: {theme}
        
        Style: {style}
        
        Include: professional aesthetics, modern design elements, clear focal point
        Exclude: people's faces, brand logos, text overlays
        
        High quality, 1200x628 aspect ratio (LinkedIn standard)
        """
        
        return prompt.strip()
    
    async def _call_replicate(self, prompt: str) -> str:
        """Call Replicate API to generate image."""
        
        if not HAS_REPLICATE:
            print("Warning: Replicate package not available, using placeholder")
            return "https://via.placeholder.com/1200x628"
        
        try:
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a60c3b36b4bab839c580fc724bccc63c521b302d402d3beed3f60303",
                input={
                    "prompt": prompt,
                    "negative_prompt": "low quality, blurry, distorted, ugly",
                    "guidance_scale": 7.5,
                    "num_inference_steps": 30,
                },
                timeout=120,
            )
            
            return output[0] if output else "https://via.placeholder.com/1200x628"
        
        except Exception as e:
            print(f"Image generation error: {e}")
            return "https://via.placeholder.com/1200x628"
