"""
Unified Prompt System - Psychology-Driven Content
===================================================
High-quality prompt templates based on LinkedIn psychology principles.
"""

from typing import Optional
from .models import PostRequest, ContentType, Tone, Audience


class PromptBuilder:
    """Build psychology-driven prompts for maximum engagement."""
    
    @staticmethod
    def build_simple_prompt(request: PostRequest) -> str:
        """Build a SIMPLE mode prompt for direct LLM generation.
        
        PSYCHOLOGY FORMULA:
        1. Pattern Interrupt Hook (1-2 lines)
        2. Relatable Struggle (1-2 lines)
        3. Transformation/Insight (1-2 lines)
        4. Tactical Value (Bullets or specifics)
        5. Soft CTA (Engagement, not sales)
        
        Args:
            request: PostRequest with topic and preferences
            
        Returns:
            Formatted prompt string
        """
        
        hook_examples = {
            ContentType.HOT_TAKE: "Most people get this wrong.",
            ContentType.EDUCATIONAL: "Here's what you need to know.",
            ContentType.FOUNDER_LESSON: "I learned this the hard way.",
            ContentType.BUILD_IN_PUBLIC: "Building in public isn't just marketing.",
        }
        
        hook = hook_examples.get(
            request.content_type,
            "Here's something worth knowing."
        )
        
        tone_instruction = PromptBuilder._get_tone_instruction(request.tone)
        audience_instruction = PromptBuilder._get_audience_instruction(
            request.audience
        )
        
        prompt = f"""You are a professional LinkedIn content creator specializing in 
scroll-stopping, conversion-focused posts.

CONTENT REQUEST:
- Topic/Achievement: {request.topic}
- Content Type: {request.content_type.value}
- Tone: {request.tone.value}
- Target Audience: {request.audience.value}
- Max Length: {request.max_length} characters

INSTRUCTIONS:
{tone_instruction}
{audience_instruction}

FORMULA (This is critical - follow exactly):
1. Start with a pattern-interrupt hook that stops scrolling
   "{hook}"
   
2. Show relatable struggle (1-2 sentences about common problem)

3. Present transformation/insight (What they learn)

4. Give tactical value (3-5 bullet points with specifics)

5. Soft CTA (Ask a question or invite engagement - NO hard selling)

CRITICAL RULES:
- Sound human, not AI
- Use short paragraphs (1-3 lines max)
- Include emojis sparingly but strategically
- Be specific (numbers, names, real examples)
- Show vulnerability with strength
- Write like you're talking to a friend
- Make readers want to respond

Generate the LinkedIn post now. Do NOT include hashtags - they'll be added separately.
Start writing immediately, no preamble."""
        
        return prompt.strip()
    
    @staticmethod
    def build_advanced_prompt(
        request: PostRequest,
        context: str,
        context_sources: list
    ) -> str:
        """Build an ADVANCED mode prompt with RAG context injection.
        
        This prompt is more detailed and context-aware.
        
        Args:
            request: PostRequest
            context: RAG-retrieved context
            context_sources: List of sources used
            
        Returns:
            Formatted prompt string
        """
        
        tone_instruction = PromptBuilder._get_tone_instruction(request.tone)
        audience_instruction = PromptBuilder._get_audience_instruction(
            request.audience
        )
        
        sources_str = "\n".join(f"- {s}" for s in context_sources[:3])
        
        prompt = f"""You are a professional LinkedIn content creator who creates posts
that convert readers to engaged followers.

CONTEXT FROM SOURCE (Use these specific details):
{context}

SOURCES USED:
{sources_str}

CONTENT REQUEST:
- Topic/Achievement: {request.topic or request.github_url}
- Content Type: {request.content_type.value}
- Tone: {request.tone.value}
- Target Audience: {request.audience.value}
- Max Length: {request.max_length} characters

INSTRUCTIONS:
{tone_instruction}
{audience_instruction}

ADVANCED FORMULA (Critical for technical content):
1. Hook with a specific insight from context (not generic)
   - Reference something unique about the project/achievement
   - Create curiosity or recognition

2. Show relatable struggle (Why does this matter to them?)

3. Demonstrate expertise (Use specifics from context)
   - Mention specific technologies, approaches, results
   - Show you deeply understand the topic

4. Transformation (What will they gain?)
   - Clear benefit or insight

5. Tactical wisdom (Actionable takeaways)
   - Specific, numbered points
   - Directly from the context/experience

6. Authority positioning (Subtle, not braggy)
   - "I've built" or "I've seen"
   - Invite deeper conversation

7. Soft CTA (Engagement)
   - Question that invites discussion
   - Reference something in the context

CRITICAL RULES:
- Use SPECIFIC details from context (repo name, technologies, etc.)
- Be concrete, not vague
- Numbers and specifics beat general statements
- Show deep understanding
- Make readers want to DM you

Generate the LinkedIn post. Do NOT include hashtags."""
        
        return prompt.strip()
    
    @staticmethod
    def _get_tone_instruction(tone: Tone) -> str:
        """Get tone-specific writing instructions."""
        instructions = {
            Tone.PROFESSIONAL: "Write in a professional but personable tone. Credible and authoritative.",
            Tone.CASUAL: "Write casually and conversationally. Like texting a smart friend.",
            Tone.ENTHUSIASTIC: "Be energetic and optimistic. Excitement about the topic is visible.",
            Tone.THOUGHTFUL: "Be reflective and nuanced. Show thinking depth.",
            Tone.BOLD: "Be direct and strong. Don't soften opinions or hedge.",
            Tone.CONVERSATIONAL: "Write like you're in a conversation. Relaxed, natural flow.",
        }
        return f"TONE: {instructions.get(tone, 'Be professional and personable.')}"
    
    @staticmethod
    def _get_audience_instruction(audience: Audience) -> str:
        """Get audience-specific writing instructions."""
        instructions = {
            Audience.FOUNDERS: "Your audience is startup founders and CEOs. Focus on growth, fundraising, and building culture.",
            Audience.DEVELOPERS: "Your audience is engineers and developers. Be technical but accessible. Focus on best practices.",
            Audience.PROFESSIONALS: "Your audience is corporate professionals. Focus on career growth, skills, and opportunity.",
            Audience.ENTREPRENEURS: "Your audience is entrepreneurs and small business owners. Focus on practical tactics and mindset.",
            Audience.TECH_LEADERS: "Your audience is CIOs and tech executives. Focus on strategy, team building, and innovation.",
            Audience.GENERAL: "Your audience is diverse professionals across industries. Keep broadly relevant.",
        }
        return f"AUDIENCE: {instructions.get(audience, 'Write for professional adults.')}"
