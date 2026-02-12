"""
Advanced RAG-Enhanced Prompts
============================
Context-injected prompts for authority positioning and lead generation.
"""


class AdvancedPrompt:
    """
    ADVANCED mode: Founder Authority Version.
    Removes AI clichés, clickbait, and fake statistics.
    Positions as someone who actually built or studied the project.
    """

    @staticmethod
    def build(request, context):
        """Build RAG-enhanced prompt with founder authority positioning."""
        
        # Get topic from request
        topic = request.topic or request.text_input or "your project"
        tone = getattr(request.tone, 'value', str(request.tone)) if hasattr(request.tone, 'value') else str(request.tone)
        audience = getattr(request.audience, 'value', str(request.audience)) if hasattr(request.audience, 'value') else str(request.audience)
        
        # Format context - extract key insights
        if hasattr(context, 'content'):
            context_str = context.content
        else:
            context_str = str(context) if context else "[Repository or project context]"
        
        return f"""
You are writing as a real founder or developer who built or deeply studied this project.

Use the context below to extract REAL insights (not summaries).

📋 CONTEXT:
{context_str}

⚠️ CRITICAL RULES - AVOID AI CLICHÉS:

❌ STRICTLY FORBIDDEN:
  • "As a seasoned leader/expert/professional"
  • "Hidden dangers", "game-changing", "revolutionary", "groundbreaking"
  • "Unlock", "the secret to", "Here's the good news"
  • Corporate buzzwords: "leverage", "synergy", "disrupt", "paradigm shift"
  • Marketing phrases: "transform your business", "next level"
  • FAKE STATISTICS: No "85% of...", no invented percentages
  • FABRICATED DATA: No made-up research, studies, or numbers
  • Fake drama or clickbait headlines
  • Generic corporate speak

✅ INSTEAD, write like lived experience:

1. **Hook (max 12 words)** - Short, sharp, honest
   • Not: "The Hidden Dangers of Open Source Projects"
   • Yes: "I spent 6 months on this. Here's what broke."

2. **Sound personal** - Use "I", "we", "you"
   • Not: "Developers face significant challenges..."
   • Yes: "I hit this wall 3 times before I figured it out."

3. **Share a real lesson or insight**
   • Extract from context, don't summarize
   • Explain why it matters
   • Be specific, not vague

4. **Keep paragraphs 1-2 lines max**
   • Mobile-first readability
   • Air between ideas

5. **Add 2-4 bullet insights if useful**
   • Tactical, not theoretical
   • Things you'd tell a friend

6. **End with soft reflection question**
   • Not: "What are your thoughts? Comment below!"
   • Yes: "Anyone else run into this?"

Topic: {topic}
Tone: {tone}
Audience: {audience}

🎯 YOUR GOAL:
Make it sound like someone who ACTUALLY built or used this.
No exaggeration. No fake authority. Just real experience.

✅ OUTPUT INSTRUCTIONS:
Write the LinkedIn post naturally without labels.
Do NOT write "POST:" or "HASHTAGS:" or "CAPTION:".
Just write the post text like a human would.
Add hashtags naturally at the bottom if relevant.
No meta-commentary. No explanations. Just the final post.
"""
