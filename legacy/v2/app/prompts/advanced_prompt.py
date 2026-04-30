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

        # Include full text_input when it's the primary content the user pasted
        text_input_val = getattr(request, 'text_input', '') or ''
        text_input_block = ""
        if text_input_val:
            text_input_block = f"""
📄 USER-PROVIDED TEXT (primary source material — extract real insights from this):
\"\"\"
{text_input_val}
\"\"\"
"""

        # Build repo-specific instruction when we have a GitHub URL
        repo_instruction = ""
        if repo_name:
            repo_instruction = f"""
🔗 GITHUB REPOSITORY: {repo_name} ({github_url})
The post MUST be specifically about this repository and its technology.
Reference actual details from the context (languages, features, architecture, README).
Do NOT write a generic post — every sentence should relate to this project.
"""

        # ---- USER INTENT (highest-priority directive) ----
        user_key_message = getattr(request, 'user_key_message', '') or ''
        key_message_block = ""
        if user_key_message:
            key_message_block = f"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 USER'S PRIMARY INTENT — THIS IS YOUR #1 DIRECTIVE      ║
╚══════════════════════════════════════════════════════════════╝
The user wants to share this specific message:

\"{user_key_message}\"

⚠️ ANCHOR EVERY SECTION TO THIS MESSAGE.
Every sentence in the post — hook, story, insight, bullets, CTA —
must connect directly to this stated intent.
The context, repo details, and text above are supporting evidence.
The user's message is the thesis. Never let supporting material
overshadow or replace the angle the user explicitly wants to convey.
"""

        # ---- TAGGING INSTRUCTIONS ----
        tags_people = getattr(request, 'tags_people', []) or []
        tags_orgs   = getattr(request, 'tags_organizations', []) or []
        tagging_block = ""
        if tags_people or tags_orgs:
            people_str = ", ".join(f"@{h}" for h in tags_people) if tags_people else "none"
            orgs_str   = ", ".join(f"@{h}" for h in tags_orgs)   if tags_orgs   else "none"
            tagging_block = f"""
🏷️ TAGGING INSTRUCTIONS:
People to tag  : {people_str}
Organizations  : {orgs_str}

Rules for tagging:
• Embed tags NATURALLY inside the post body — never dump them at the end.
• Tag a person when acknowledging collaboration, attribution, or shared expertise.
  Example: "Working alongside @JaneDoe on this changed how I think about architecture."
• Tag an organization when referencing their platform, tools, community, or contribution.
  Example: "The @OpenAI API made this prototype possible in under a week."
• Limit to ONE tag per paragraph — avoid clustering multiple handles together.
• If a tag has no natural context fit, skip it — forced tags hurt readability.
"""

        return f"""
You are writing as a real founder or developer who built or deeply studied this project.

Use the context below to extract REAL insights (not summaries).
{key_message_block}
{repo_instruction}
📋 CONTEXT:
{context_str}
{text_input_block}
{tagging_block}
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

✅ WRITE LIKE LIVED EXPERIENCE:

1. **Hook (max 12 words)** - Short, sharp, honest — tied to the user's key message
   • Not: "The Hidden Dangers of Open Source Projects"
   • Yes: "I spent 6 months on this. Here's what broke."

2. **Sound personal** - Use "I", "we", "you"
   • Not: "Developers face significant challenges..."
   • Yes: "I hit this wall 3 times before I figured it out."

3. **Share the real lesson or insight from the user's stated message**
   • Extract from context and user intent, don't just summarize
   • Explain why it matters specifically to the audience
   • Be specific, not vague

4. **Keep paragraphs 1-2 lines max**
   • Mobile-first readability
   • Air between ideas

5. **Add 2-4 bullet insights if useful**
   • Tactical, not theoretical
   • Things you'd tell a friend

6. **End with a soft reflection question**
   • Not: "What are your thoughts? Comment below!"
   • Yes: "Anyone else run into this?"

Topic: {topic}
Tone: {tone}
Audience: {audience}

🎯 YOUR GOAL:
Make it sound like someone who ACTUALLY built or used this AND has a specific point to make.
No exaggeration. No fake authority. Just real experience aligned with the user's intent.

✅ OUTPUT INSTRUCTIONS:
Write the LinkedIn post naturally without labels.
Do NOT write "POST:" or "HASHTAGS:" or "CAPTION:".
Just write the post text like a human would.
Add hashtags naturally at the bottom if relevant.
No meta-commentary. No explanations. Just the final post.
"""
