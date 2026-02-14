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
        
        # Get topic from request — prefer github_url-derived name when available
        github_url = getattr(request, 'github_url', '') or ''
        repo_name = ''
        if github_url:
            # Extract owner/repo from URL for explicit mention
            parts = github_url.rstrip('/').split('/')
            if len(parts) >= 2:
                repo_name = f"{parts[-2]}/{parts[-1]}"
        
        topic = request.topic or repo_name or request.text_input or "your project"
        tone = getattr(request.tone, 'value', str(request.tone)) if hasattr(request.tone, 'value') else str(request.tone)
        audience = getattr(request.audience, 'value', str(request.audience)) if hasattr(request.audience, 'value') else str(request.audience)
        
        # Format context - extract key insights
        if hasattr(context, 'content'):
            context_str = context.content
        else:
            context_str = str(context) if context else "[Repository or project context]"
        
        # Build repo-specific instruction when we have a GitHub URL
        repo_instruction = ""
        if repo_name:
            repo_instruction = f"""
🔗 GITHUB REPOSITORY: {repo_name} ({github_url})
The post MUST be specifically about this repository and its technology.
Reference actual details from the context (languages, features, architecture, README).
Do NOT write a generic post — every sentence should relate to this project.
"""
        
        return f"""
You are writing as a real founder or developer who built or deeply studied this project.

Use the context below to extract REAL insights (not summaries).
{repo_instruction}
📋 CONTEXT:
{context_str}

⚠️ CRITICAL ANTI-HALLUCINATION & AUTHENTICITY RULES:

🚫 STRICTLY FORBIDDEN - NEVER FABRICATE:
  • "As a seasoned leader/expert/professional"
  • "Hidden dangers", "game-changing", "revolutionary", "groundbreaking"
  • "Unlock", "the secret to", "Here's the good news"
  • Corporate buzzwords: "leverage", "synergy", "disrupt", "paradigm shift"
  • Marketing phrases: "transform your business", "next level"
  • FAKE STATISTICS: No "85% of...", no invented percentages, no "94% correlation"
  • FABRICATED DATA: No made-up research, studies, or numbers
  • INVENTED METRICS: No "improved by X%" unless in context
  • FALSE EXPERTISE CLAIMS: No "studies show", "research indicates", "experts say"
  • Fake drama or clickbait headlines
  • Generic corporate speak
  • Made-up before/after comparisons
  • Exaggerated timelines or costs not in context

✅ VERIFIED INFORMATION ONLY:
  • ONLY use numbers/data explicitly mentioned in context below
  • If no specific metrics provided, use qualitative insights
  • Share frameworks and principles instead of fake statistics
  • Write from genuine understanding, not fabricated authority
  • Be informational through deep explanations, not invented proof
  • Sound like a real person who built/studied this, not a marketing bot

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
