"""
Base LinkedIn Prompts - High-Converting Templates
===============================================
Master prompt templates for engaging LinkedIn content.
Based on high-performing patterns from top LinkedIn creators.
"""

from typing import Dict, Any
from core.models import PostRequest, RAGContext


def build_simple_prompt(request: PostRequest) -> str:
    """
    Build high-converting prompt for simple mode generation.
    
    This is the MASTER LinkedIn prompt that creates scroll-stopping content.
    """
    
    # Get display names for user-friendly prompting
    from core.models import get_tone_display_names, get_audience_display_names
    
    tone_name = get_tone_display_names().get(request.tone.value, request.tone.value)
    audience_name = get_audience_display_names().get(request.audience.value, request.audience.value)
    
    prompt = f"""
You are a high-performing LinkedIn creator with 100K+ followers who writes scroll-stopping content.

⚠️ CRITICAL ANTI-HALLUCINATION RULES:
🚫 NEVER fabricate statistics, percentages, or research claims
🚫 NEVER invent "studies show" or "research indicates" without real sources
🚫 NEVER make up specific numbers not provided in the topic/context
✅ ONLY use data explicitly mentioned in the topic/context below
✅ Provide value through frameworks, insights, and practical advice
✅ Write like a real professional sharing genuine experience
✅ Be informational through explanations and principles, not fake metrics

Your job is to write a LinkedIn post that:
- Feels authentically human, not AI-generated
- Uses short, punchy lines for mobile readability  
- Creates immediate curiosity with a pattern-interrupt hook
- Delivers genuine insights that professionals care about
- Attracts {audience_name.lower()}
- Drives meaningful engagement and conversation
- SOUNDS NATURAL like a conversation with a smart colleague

CRITICAL WRITING RULES:
• Max 1-2 sentences per paragraph (mobile-first)
• Use strategic whitespace for visual breathing room
• Strong hook in the first line - no boring openers, but keep it honest
• NO clichés like "In today's fast-paced world" or "I'm excited to announce"
• NO generic corporate speak or buzzwords
• NO fabricated statistics to sound authoritative
• Conversational but professional tone - like explaining to a colleague
• Share real insights, frameworks, and principles
• Slightly bold opinions but not arrogant or exaggerated
• Make every line count - cut the fluff

POST STRUCTURE THAT CONVERTS:
1. HOOK: Pattern interrupt that stops the scroll (question, contrarian take, surprising stat, personal story opener)
2. CONTEXT: Brief setup or story that relates to your audience  
3. INSIGHT: The "aha moment" or key realization
4. VALUE: 3-5 actionable takeaways (if educational content)
5. ENGAGEMENT: Soft CTA that invites conversation (question or discussion prompt)

TOPIC/INPUT:
{request.topic or request.text_input}

TARGET TONE:
{tone_name} - Make it feel natural for this tone

TARGET AUDIENCE:  
{audience_name}

CONTENT FOCUS:
Write about the topic in a way that provides real value to your audience. Share insights, lessons learned, or actionable advice that they can apply in their work or career.

Now write a LinkedIn post that would make people stop scrolling, think "this is useful," and want to engage in the comments.

FORMAT YOUR RESPONSE AS:

POST:
[Your compelling LinkedIn post here]

HASHTAGS:
[5-8 relevant professional hashtags]

CAPTION:
[Brief description of what the post is about - only if requested]
"""
    
    return prompt.strip()


def build_rag_prompt(request: PostRequest, context: RAGContext) -> str:
    """
    Build enhanced prompt using RAG context for higher quality.
    """
    
    from core.models import get_tone_display_names, get_audience_display_names
    
    tone_name = get_tone_display_names().get(request.tone.value, request.tone.value)
    audience_name = get_audience_display_names().get(request.audience.value, request.audience.value)
    
    prompt = f"""
You are an expert LinkedIn content creator who transforms complex information into engaging, scroll-stopping posts.

Your mission: Create a LinkedIn post that turns the provided context into valuable content for {audience_name.lower()}.

CONTEXT TO WORK WITH:
{context.content}

WRITING APPROACH:
Extract genuine insights from the context and present them naturally:
- Highlight why this matters to professionals
- Show the bigger picture implications  
- Provide actionable frameworks and principles
- Share practical how-to guidance
- Spark curiosity and discussion
- Write like you're explaining this to a colleague over coffee

⚠️ FACT-CHECK REQUIREMENTS:
• ONLY use specific data/numbers if they appear in the context below
• If context lacks numbers, provide value through frameworks and insights
• Never fabricate percentages or statistics to sound credible
• Ground every claim in the context provided or general professional knowledge
• Be informational through explanation, not invented metrics

LINKEDIN SUCCESS FORMULA:
• Start with an authentic hook that stops the scroll (no exaggeration)
• Extract 1-2 key insights from the context
• Make it relevant to your audience's daily challenges
• Explain the WHY and HOW, not just the WHAT
• Share practical approaches and frameworks
• End with a question that drives engagement
• Use short lines and strategic whitespace
• Sound like a knowledgeable human, not a content bot

TARGET DETAILS:
- Tone: {tone_name}
- Audience: {audience_name}
- Topic: {request.topic}

CRITICAL: Don't just summarize. Find valuable insights and explain them naturally, as if you're teaching a smart colleague. Use ONLY verified information from the context.

FORMAT YOUR RESPONSE AS:

POST:
[Your engaging LinkedIn post based on the context]

HASHTAGS:  
[5-8 relevant hashtags that would help this post get discovered]

CAPTION:
[Brief engaging description - only if requested]
"""
    
    return prompt.strip()


def build_refinement_prompt(original_post: str, feedback: str = None) -> str:
    """
    Build prompt for post refinement to improve engagement potential.
    
    This is the "second-pass refinement" that significantly improves quality.
    """
    
    refinement_instructions = feedback or """
    Make this LinkedIn post more scroll-stopping by:
    - Creating a stronger, more curiosity-driven hook
    - Removing any generic corporate language
    - Improving the reading rhythm with better line breaks
    - Adding more specific, actionable value  
    - Making it feel more conversational and human
    - Ensuring it drives engagement and comments
    """
    
    prompt = f"""
You are a LinkedIn engagement expert who optimizes posts for maximum scroll-stopping power.

REFINEMENT GOAL:
Transform this LinkedIn post to significantly increase engagement, shares, and meaningful comments.

{refinement_instructions}

ORIGINAL POST:
{original_post}

OPTIMIZATION PRINCIPLES:
• Hook must create immediate curiosity 
• Every line should add value or advance the story
• Remove corporate buzzwords and clichés
• Use conversational language that builds connection
• Include specific examples over vague statements
• End with a question that people actually want to answer
• Optimize for mobile reading (short lines, white space)

Keep the core message but make it irresistible to engage with.

REFINED POST:
"""
    
    return prompt.strip()


# Content-type specific prompt builders
def build_educational_prompt(request: PostRequest) -> str:
    """Prompt optimized for educational content."""
    
    base = build_simple_prompt(request)
    
    educational_enhancement = """

EDUCATIONAL CONTENT FOCUS:
This should be a knowledge-sharing post that:
- Breaks down complex topics into digestible insights
- Provides immediately actionable advice
- Uses numbered lists or bullet points for clarity
- Positions you as a helpful expert, not a show-off
- Includes specific examples or case studies
- Ends with a question that tests understanding or asks for experiences

Make it the kind of post people bookmark and share with colleagues.
"""
    
    return base + educational_enhancement


def build_story_prompt(request: PostRequest) -> str:
    """Prompt optimized for storytelling content."""
    
    base = build_simple_prompt(request)
    
    story_enhancement = """

STORYTELLING FOCUS:
This should be a narrative-driven post that:
- Opens with a compelling scene or moment
- Builds tension or curiosity throughout
- Connects the story to a broader professional lesson
- Uses sensory details to make it vivid
- Reveals insights through the narrative, not by stating them
- Ends by connecting the story to the reader's experience

Make people feel like they're right there with you in the story.
"""
    
    return base + story_enhancement


def build_hot_take_prompt(request: PostRequest) -> str:
    """Prompt optimized for contrarian/hot take content."""
    
    base = build_simple_prompt(request)
    
    hot_take_enhancement = """

HOT TAKE FOCUS:
This should be a thought-provoking post that:
- Challenges conventional wisdom in your field
- Presents a contrarian viewpoint backed by evidence or experience
- Makes people think "I never considered that angle"
- Sparks healthy debate in the comments
- Shows confidence without being arrogant
- Backs up bold claims with specific reasoning

Make it the kind of post that generates 100+ thoughtful comments.
"""
    
    return base + hot_take_enhancement


# Prompt routing function
def route_prompt(request: PostRequest, context: RAGContext = None) -> str:
    """
    Route to appropriate prompt based on content type and context availability.
    """
    
    # If we have RAG context, use enhanced prompts
    if context:
        return build_rag_prompt(request, context)
    
    # Route simple prompts by content type
    content_type = request.content_type.value
    
    if content_type == "educational":
        return build_educational_prompt(request)
    elif content_type in ["hot_take", "founder_lesson"]:
        return build_hot_take_prompt(request)  
    elif content_type in ["learning_share", "build_in_public"]:
        return build_story_prompt(request)
    else:
        return build_simple_prompt(request)


# Template validation
def validate_prompt_output(generated_content: str) -> Dict[str, bool]:
    """
    Validate that generated content follows LinkedIn best practices.
    """
    
    lines = generated_content.split('\n')
    
    validation = {
        "has_hook": len(lines) > 0 and len(lines[0]) > 10,
        "appropriate_length": 100 <= len(generated_content) <= 3000,
        "has_whitespace": '\n\n' in generated_content,
        "no_cliches": not any(
            cliche in generated_content.lower() 
            for cliche in ["excited to announce", "fast-paced world", "game changer"]
        ),
        "ends_with_engagement": generated_content.strip().endswith('?')
    }
    
    return validation


if __name__ == "__main__":
    # Test prompt building
    from core.models import PostRequest, ContentType, Tone, Audience
    
    test_request = PostRequest(
        content_type=ContentType.EDUCATIONAL,
        topic="The future of AI in software development",
        tone=Tone.THOUGHTFUL,
        audience=Audience.DEVELOPERS
    )
    
    prompt = build_simple_prompt(test_request)
    print("Generated prompt length:", len(prompt))
    print("Prompt preview:", prompt[:200] + "...")