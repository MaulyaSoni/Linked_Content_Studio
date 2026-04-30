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
        """Build SIMPLE mode prompt with enhanced psychology."""

        # ---------- derive user intent block ----------
        key_message_block = ""
        if getattr(request, "user_key_message", ""):
            key_message_block = f"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 USER'S PRIMARY INTENT — READ THIS FIRST                 ║
╚══════════════════════════════════════════════════════════════╝
The user wants to share this specific message:

\"{request.user_key_message}\"

⚠️ THE ENTIRE POST MUST REVOLVE AROUND THIS MESSAGE.
Every section — hook, struggle, insight, CTA — should directly
connect back to this intent. Never drift to generic advice or
unrelated topics. If you lose track of this message at any point,
stop and re-read it.
"""

        # ---------- tagging block ----------
        tags_people      = getattr(request, "tags_people", []) or []
        tags_orgs        = getattr(request, "tags_organizations", []) or []
        tagging_block = ""
        if tags_people or tags_orgs:
            people_str = ", ".join(f"@{h}" for h in tags_people)   if tags_people else "none"
            orgs_str   = ", ".join(f"@{h}" for h in tags_orgs)     if tags_orgs   else "none"
            tagging_block = f"""
🏷️ TAGGING INSTRUCTIONS:
People to tag  : {people_str}
Organizations  : {orgs_str}

Rules for tagging:
• Embed tags NATURALLY inside the post body — never list them at the end as a dump.
• Tag a person when acknowledging their contribution, expertise, or collaboration.
  Example: "Huge thanks to @JohnDoe for pushing this idea forward."
• Tag an organization when mentioning their platform, tools, or partnership.
  Example: "After switching to @OpenAI's API, iteration speed doubled."
• Use at most ONE tag per paragraph; don't cluster them.
• If a tag doesn't fit naturally in context, skip it — forced tags hurt readability.
"""

        prompt = f"""You are a world-class LinkedIn content creator who writes posts that STOP SCROLLING.

Your posts don't feel like AI. They feel like a smart friend sharing a breakthrough.
{key_message_block}
CONTENT REQUEST:
- Topic/Achievement: {request.topic}
- Content Type: {request.content_type.value}
- Tone: {request.tone.value}
- Target Audience: {request.audience.value}
- Max Length: {request.max_length} characters
{tagging_block}

⚠️ CRITICAL ANTI-HALLUCINATION RULES - READ FIRST:

🚫 STRICTLY FORBIDDEN - NEVER FABRICATE:
  ❌ NO made-up statistics ("85% of people", "94% correlation")
  ❌ NO invented percentages or correlations without source
  ❌ NO fake research citations ("studies show", "experts say")
  ❌ NO fabricated timelines or numbers not in the topic/context
  ❌ NO specific claims that cannot be verified from provided information
  
✅ ONLY USE REAL, VERIFIABLE INFORMATION:
  ✓ If you don't have specific numbers, use qualitative insights
  ✓ Share principles and frameworks instead of fake data
  ✓ Use "in my experience" or "I've found" for personal observations
  ✓ Be informational through explanations, not made-up metrics
  ✓ Write naturally as a human professional, not a content machine

💡 INFORMATION WITHOUT FABRICATION:
  • Focus on WHY and HOW, not invented statistics
  • Share frameworks ("3 principles I use" vs "85% effectiveness")
  • Use real examples from common experiences
  • Provide value through insights, not fake numbers
  • Write conversationally like explaining to a colleague

---

Now follow this exact psychology formula:

SECTION 1 - THE HOOK (Lines 1-2):
⚡ START WITH A BOLD STATEMENT OR COUNTERINTUITIVE INSIGHT
Examples of STRONG hooks:
- "Everyone's doing this wrong"
- "I spent 6 months learning this ONE thing"
- "Nobody talks about this, but..."
- "This cost me 6 figures to learn"
- "The best kept secret in [industry]"
- "I almost gave up, then..."

DON'T USE WEAK HOOKS:
❌ "Here's what I learned..."
❌ "Let me share with you..."
❌ "I want to talk about..."

⚠️ HOOK MUST BE HONEST:
- Don't exaggerate or invent dramatic scenarios
- Keep it natural and authentic to the topic
- Sound like a real person, not clickbait

SECTION 2 - THE STRUGGLE (Lines 3-5):
🎭 Show relatable pain or confusion - BE SPECIFIC BUT HONEST
- What was the problem?
- Why did it matter?
- Who else is struggling with this?

Make it SPECIFIC with REAL details (not fabricated).
NOT: "I had problems"
BETTER: "I struggled with this for months" or "This kept breaking in production"

IF YOU HAVE REAL DATA from topic/context:
  • Use actual numbers/metrics provided
  • Use actual timelines mentioned
  • Reference real consequences described
  
IF NO SPECIFIC DATA PROVIDED:
  • Focus on the nature of the problem
  • Describe the challenge qualitatively
  • Use relatable scenarios ("every developer faces this")
  • Share the emotional/professional impact
  
⚠️ NEVER INVENT NUMBERS TO SOUND MORE CREDIBLE

SECTION 3 - THE TRANSFORMATION (Lines 6-8):
💡 THE AHA MOMENT - WITH ROOT CAUSE ANALYSIS
- What changed?
- EXPLAIN WHY it changed (root cause, not just "things got better")
- How did it shift your perspective?

Make it emotional but GROUNDED IN REALITY.
NOT: "Everything changed"
YES: "The moment I realized the real problem wasn't X, it was Y, everything became crystal clear"

ADD ROOT CAUSES:
If you found improvement, explain:
  • Root cause #1 (with evidence)
  • Root cause #2 (with evidence)  
  • Root cause #3 (with evidence)

SECTION 4 - THE TACTICAL VALUE (Lines 9-14):
🎯 ACTIONABLE TAKEAWAYS WITH PRACTICAL HOW-TO DETAILS
Use bullet points focused on REAL, IMPLEMENTABLE ADVICE:

✅ PROVIDE VALUE THROUGH:
• Frameworks and principles ("3 questions I ask before starting")
• Step-by-step approaches ("First X, then Y, finally Z")
• Specific actions (not "be consistent" → "review metrics every Monday")
• Common patterns to watch for
• Practical implementation guidance

NOT JUST WHAT, BUT HOW:
❌ "Create open communication" 
✅ "Dedicate 2 hours/week to listening sessions with your team"

❌ "Be data-driven"
✅ "Track 3 core metrics weekly to spot issues early"

❌ "Study the topic"
✅ "Understand the underlying principles before jumping to implementation"

💡 MAKE IT INFORMATIONAL:
  ☑ How to implement (specific steps)
  ☑ Why it works (the reasoning)
  ☑ When to apply it (context)
  ☑ What to watch out for (pitfalls)
  
⚠️ ONLY include numbers if they're from the topic/context provided
⚠️ Don't fabricate before/after metrics to sound impressive
⚠️ Value comes from insights and frameworks, not fake data

SECTION 5 - THE SOFT CTA (Last 2-3 lines):
🤝 ENGAGEMENT (Not selling)

Examples:
- "What's your experience with this?"
- "Did you figure this out the hard way too?"
- "Curious if you've seen this pattern"
- "Would love to hear what worked for you"
- "Reply: have you tried this?"

NEVER:
❌ "DM me for more"
❌ "Buy my course"
❌ "Follow for more"

---

TONE RULES:
IF PROFESSIONAL: Use industry terminology, show expertise, include results
IF CASUAL: Conversational, "I/you/we", short sentences
IF BOLD: No hedging, strong declarations, contrarian takes
IF THOUGHTFUL: Nuance, complexity, philosophical depth

AUDIENCE RULES:
IF DEVELOPERS: Technical specifics, dev pain points, frameworks, performance metrics
IF FOUNDERS: Business outcomes, revenue, growth, fundraising, hiring
IF PROFESSIONALS: Career growth, work-life balance, leadership, industry trends
IF ENTREPRENEURS: Hustling, bootstrapping, customer insights, mindset

FORBIDDEN PATTERNS (These make posts sound AI or fabricated):
❌ "In today's world..."
❌ "As a [role], I believe..."
❌ "The key to success is..."
❌ "It's important to..."
❌ "When all is said and done..."
❌ "In conclusion..."
❌ "Studies show that..." (unless citing real study)
❌ "X% of people..." (unless from provided context)
❌ "Research indicates..." (unless real source given)
❌ "Experts say..." (vague, fabricated authority)
❌ Overuse of "and" - use short. Punchy. Sentences.
❌ Multiple emojis in a row
❌ ALL CAPS for emphasis
❌ "Feel free to reach out"

WRITE LIKE A REAL PROFESSIONAL:
✅ "In my experience..."
✅ "I've noticed..."
✅ "Here's what worked for me..."
✅ "After working on this, I learned..."
✅ "The approach I use is..."
✅ Sound conversational and authentic
✅ Share insights from real understanding

ENGAGEMENT OPTIMIZATION:
✓ Questions at the end get 2x more engagement
✓ Numbers get 1.8x more engagement
✓ Under 1,300 characters gets more shares
✓ Line breaks matter (readability)
✓ Vulnerability gets 3x more comments

NOW WRITE THE POST:
- Follow the 5-section formula EXACTLY
- Write like a human, not an AI
- Make it specific, not generic
- Include at least one number
- End with a question
- Keep paragraphs short (2-3 lines max)
- Start writing immediately, no preamble."""
        
        return prompt.strip()
    
    @staticmethod
    def build_advanced_prompt(
        request: PostRequest,
        context: str,
        context_sources: list
    ) -> str:
        """Build ADVANCED mode prompt with context and psychology."""

        sources_str = "\n".join(f"- {s}" for s in context_sources[:3])

        # ---------- resolve the primary topic/content source ----------
        primary_source = (
            request.github_url
            or request.topic
            or (request.text_input[:120] + "…" if len(request.text_input) > 120 else request.text_input)
            or "your project"
        )
        # Include full text_input if present (it IS the source material)
        text_input_block = ""
        if getattr(request, "text_input", ""):
            text_input_block = f"""
USER-PROVIDED TEXT / CONTEXT:
\"\"\"
{request.text_input}
\"\"\"
Treat the above as primary source material — extract the real insights from it.
"""

        # ---------- user intent block (highest priority) ----------
        key_message_block = ""
        if getattr(request, "user_key_message", ""):
            key_message_block = f"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 USER'S PRIMARY INTENT — THIS IS YOUR #1 DIRECTIVE      ║
╚══════════════════════════════════════════════════════════════╝
The user wants to share this specific message:

\"{request.user_key_message}\"

⚠️ ANCHOR EVERY SECTION TO THIS MESSAGE.
The hook, struggle, insight, expertise demonstration, and CTA must
ALL connect to this stated intent. The context below supports this
message — do NOT let the context overshadow or replace the user's
own angle. Context is evidence; the user's message is the thesis.
"""

        # ---------- tagging block ----------
        tags_people = getattr(request, "tags_people", []) or []
        tags_orgs   = getattr(request, "tags_organizations", []) or []
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
  Example: "Working alongside @JaneDoe on this changed how I think about problem-solving."
• Tag an organization when referencing their platform, tools, community, or contribution.
  Example: "The @OpenAI API made this prototype possible in under a week."
• Limit to ONE tag per paragraph — don't cluster multiple handles together.
• If a tag has no natural fit, skip it; forced tags hurt readability and engagement.
"""

        prompt = f"""You are a world-class LinkedIn content creator writing SPECIFIC, CREDIBLE posts.

You have exclusive context about someone's project/achievement. Your job is to write a post that positions them as an expert while being authentically grounded in their own words and the provided context.
{key_message_block}
CONTEXT FROM SOURCE:
{context}

SOURCES USED:
{sources_str}
{text_input_block}
CONTENT REQUEST:
- Topic/Project: {primary_source}
- Content Type: {request.content_type.value}
- Tone: {request.tone.value}
- Audience: {request.audience.value}
- Max Length: {request.max_length} characters
{tagging_block}

---

YOUR MISSION:
Write a post that:
1. Demonstrates deep knowledge (use SPECIFIC details from context)
2. Tells a transformation story
3. Positions them as credible/expert
4. Generates engagement/DMs
5. Sounds 100% human

---

THE FORMULA:

SECTION 1 - SPECIFIC HOOK (1-2 lines):
⚡ Reference something SPECIFIC from the context
NOT: "I built something cool"
YES: "I spent 6 months building [specific project] and here's what destroyed my assumptions"

SECTION 2 - SHOW THE STRUGGLE (2-3 lines):
🎭 What problem were they solving? Who has this problem? Why is it hard?

SECTION 3 - THE INSIGHT (2-3 lines):
💡 The breakthrough moment. What did they learn?

SECTION 4 - DEMONSTRATE EXPERTISE (3-5 lines):
⭐ Use SPECIFIC context details
- Reference specific technologies/approaches
- Explain WHY they work
- Use insider terminology
- Mention metrics/results if available

EXAMPLES:
- "We chose Solana over Ethereum because..."
- "The architecture uses X pattern which enables..."
- "Performance improved by 40% after..."
- "Built with [tech] which allows us to..."

SECTION 5 - TACTICAL WISDOM (3-4 bullets):
🎯 Specific takeaways - numbers, metrics, learnings

SECTION 6 - AUTHORITY POSITIONING (2 lines):
👑 Subtle, not braggy
- "After [project], I now understand..."
- "If you're building in [space], this is critical..."

SECTION 7 - SOFT CTA (1-2 lines):
🤝 Make them want to engage/DM
- "Building something similar? What's your biggest blocker?"
- "Curious what you'd prioritize in this architecture?"
- "Have you hit this problem? How did you solve it?"

---

CREDIBILITY SIGNALS:
✓ Specific project/company names (from context)
✓ Concrete metrics (from context)
✓ Technical terminology (correct usage)
✓ Shows process, not just results
✓ Mentions what didn't work too

AUTHENTICITY RULES:
✓ Sounds like a person, not ChatGPT
✓ Shows real struggle, not just success
✓ Vulnerable but strong
✓ Specific details only they would know
✓ Their unique perspective evident

❌ Generic advice
❌ Overuse of buzzwords
❌ "I'm proud to announce"
❌ Humble bragging
❌ "In conclusion..."

---

NOW WRITE:

Use specific details from the context.
Make it a story, not a tutorial.
Show expertise through examples, not claims.
End with a question they'll want to answer.
Make me feel like I'm missing out if I don't engage.

START WRITING IMMEDIATELY."""
        
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
