"""
LinkedIn Psychology-Driven Prompts
===================================
Simple Mode: No RAG, pure prompt engineering with viral psychology.
Advanced Mode: Context-injected prompts with authority positioning.
"""

from prompts.advanced_prompt import AdvancedPrompt


class SimplePrompt:
    """
    Psychology-driven prompt for SIMPLE mode (no RAG).
    Based on viral LinkedIn patterns:
    - Pattern interrupt hooks
    - Emotional storytelling  
    - Short punchy sentences
    - Soft CTAs for engagement
    """

    @staticmethod
    def build(request):
        """Build psychology-optimized simple prompt."""
        
        # Get topic from request
        topic = request.topic or request.text_input or "your area of expertise"
        tone = getattr(request.tone, 'value', str(request.tone)) if hasattr(request.tone, 'value') else str(request.tone)
        audience = getattr(request.audience, 'value', str(request.audience)) if hasattr(request.audience, 'value') else str(request.audience)
        
        return f"""
You are a top LinkedIn ghostwriter who creates viral, high-engagement posts.

🎯 PSYCHOLOGY FORMULA:
1. Pattern Interrupt Hook (2 lines max) - Create curiosity or shock
2. Relatable Struggle - Connect with pain points
3. Transformation/Insight - The "aha" moment
4. Tactical Value - Bullet points, actionable
5. Soft Engagement CTA - No hard sells

📝 WRITING RULES:
• Hook that stops the scroll (first 2 lines)
• Short paragraphs (1-2 lines)
• Natural, conversational tone
• Emotional storytelling
• Bullet points for clarity
• No corporate jargon
• Sound human, not AI
• Slightly bold and opinionated
• Position as credible expert (subtle authority)

❌ STRICTLY FORBIDDEN:
• Generic motivational quotes
• AI-sounding phrases ("game-changing", "unlock", "the secret to")
• Long paragraphs
• Salesy language
• Corporate buzzwords ("leverage", "synergy", "disruption")
• Marketing speak ("Here's the good news", "The truth is")
• FAKE STATISTICS (no "85% of employees...", no invented percentages)
• FABRICATED RESEARCH (no made-up studies or data)
• Over-explaining

Topic: {topic}
Tone: {tone}
Audience: {audience}

✅ OUTPUT INSTRUCTIONS:
Write the LinkedIn post naturally.
Do NOT use labels like "POST:" or "HASHTAGS:".
Just write the post text, then add hashtags at the bottom.
Keep it authentic and human.

Create a post that sounds like a real person writing on LinkedIn, not AI-generated content.
"""


def build_prompt(request, context=None):
    """
    Smart prompt builder - routes to SIMPLE or ADVANCED based on context.
    
    Args:
        request: PostRequest with topic, tone, audience
        context: Optional RAG context (if provided, uses ADVANCED mode)
    
    Returns:
        Optimized prompt string
    """
    
    # ADVANCED MODE - Context available from RAG
    if context is not None and hasattr(context, 'content') and context.content:
        return AdvancedPrompt.build(request, context)
    
    # SIMPLE MODE - No RAG, pure psychology
    return SimplePrompt.build(request)
