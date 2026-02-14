# ============================================================================
# QUALITY CHAINS - INFORMATION DENSITY & SPECIFICITY
# ============================================================================
"""
Quality improvement chains for LinkedIn post generation.
Adds specificity, grounds claims in context, and scores post quality.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from core.llm import get_llm_deterministic, get_llm

# ============================================================================
# LAZY CHAIN INITIALIZATION
# ============================================================================
# Chains are created on first use, not at module import time.
# This prevents unnecessary API connections during imports.

_specificity_enforcer = None
_quality_scorer = None
_hook_generator = None
_context_grounder = None

def _get_specificity_enforcer():
    """Get or create specificity enforcer chain."""
    global _specificity_enforcer
    if _specificity_enforcer is None:
        prompt = PromptTemplate.from_template(SPECIFICITY_CHECK_PROMPT)
        llm = get_llm_deterministic()
        _specificity_enforcer = prompt | llm
    return _specificity_enforcer

def _get_quality_scorer():
    """Get or create quality scorer chain."""
    global _quality_scorer
    if _quality_scorer is None:
        prompt = PromptTemplate.from_template(QUALITY_SCORE_PROMPT)
        llm = get_llm_deterministic()
        _quality_scorer = prompt | llm
    return _quality_scorer

def _get_hook_generator():
    """Get or create hook generator chain."""
    global _hook_generator
    if _hook_generator is None:
        prompt = PromptTemplate.from_template(HOOK_OPTIONS_PROMPT)
        llm = get_llm_deterministic()
        _hook_generator = prompt | llm
    return _hook_generator

def _get_context_grounder():
    """Get or create context grounder chain."""
    global _context_grounder
    if _context_grounder is None:
        prompt = PromptTemplate.from_template(CONTEXT_GROUNDING_PROMPT)
        llm = get_llm_deterministic()
        _context_grounder = prompt | llm
    return _context_grounder


# ============================================================================
# 1. SPECIFICITY ENFORCER CHAIN
# ============================================================================

SPECIFICITY_CHECK_PROMPT = """You are an editor improving LinkedIn posts for SPECIFICITY and NATURAL LANGUAGE.

Review this post and improve it by:
1. Replacing vague phrases with concrete, practical details
2. Adding frameworks and principles (not invented metrics)
3. Removing generic filler lines
4. Making it sound like a knowledgeable professional wrote it
5. Ensuring claims are honest and implementable

POST TO IMPROVE:
{post}

CONSTRAINTS:
- Keep the same length (max 5% longer)
- Preserve the emotional core and authenticity
- DON'T invent numbers or statistics - remove them if unverifiable
- Add specificity through HOW-TO details and frameworks
- Maintain conversational, human tone
- Focus on being informational through explanation, not fake data

OUTPUT:
Return ONLY the improved post, exactly formatted (no explanation or meta-commentary).

QUALITY CHECKLIST:
✓ Specific, actionable advice ("be consistent" → "review metrics every Monday")
✓ No vague phrases ("it was great" → "the approach simplified our workflow")
✓ At least 2 specific HOW-TO details or principles
✓ Frameworks readers can apply ("3 questions I ask", "the pattern I use")
✓ No invented statistics or fake research
✓ Expertise shown through practical insights, not fabricated claims
✓ Sounds like a real professional, not a content machine

IMPROVE NOW (return clean post only):"""

def enforce_specificity(post: str) -> str:
    """Improve post specificity and ground it in reality."""
    chain = _get_specificity_enforcer()
    result = chain.invoke({"post": post})
    return result.content if hasattr(result, 'content') else str(result)

# ============================================================================
# 2. QUALITY SCORER CHAIN
# ============================================================================

QUALITY_SCORE_PROMPT = """You are a LinkedIn post quality evaluator.

Score this post from 1-10 SEPARATELY on:

POST:
{post}

---

EVALUATION CRITERIA:

1. CLARITY (1-10)
   - Is it easy to understand?
   - Does each section flow logically?
   - Are sentences short and punchy?

2. SPECIFICITY (1-10)
   - Are claims backed by numbers/examples?
   - Does it show expertise through details?
   - No vague phrases like "it was great"?

3. ENGAGEMENT POTENTIAL (1-10)
   - Would people want to comment?
   - Does it end with an interesting question?
   - Does it create curiosity or emotion?

4. CREDIBILITY (1-10)
   - Does the writer sound authentic?
   - Are claims believable/grounded in reality?
   - Does it show real experience, not theory?

5. ACTIONABILITY (1-10)
   - Can readers extract lessons/tactics?
   - Are insights specific and applicable?
   - Would someone take action based on this?

---

RESPONSE FORMAT (EXACT):

Clarity: [X]/10 - [1 sentence explanation]
Specificity: [X]/10 - [1 sentence explanation]
Engagement: [X]/10 - [1 sentence explanation]
Credibility: [X]/10 - [1 sentence explanation]
Actionability: [X]/10 - [1 sentence explanation]

Overall: [AVERAGE]/10

[2-3 sentence summary of post quality]

TOP IMPROVEMENT: [1 specific thing that would most improve this post]"""

def score_post_quality(post: str) -> str:
    """Score post on multiple quality dimensions."""
    chain = _get_quality_scorer()
    result = chain.invoke({"post": post})
    return result.content if hasattr(result, 'content') else str(result)

# ============================================================================
# 3. HOOK GENERATOR CHAIN (3 options)
# ============================================================================

HOOK_OPTIONS_PROMPT = """Generate 3 DIFFERENT LinkedIn hooks for this topic.

Each hook must be SPECIFIC and STOP SCROLLING.

TOPIC: {topic}
CONTEXT: {context}
TONE: {tone}
AUDIENCE: {audience}

---

GENERATE 3 HOOKS:

Hook #1 (CURIOSITY STYLE - makes them question assumptions):
- Start with: "Everyone's doing this...", "I thought...", "The problem is...", "Nobody talks about..."
- Example: "I thought performance was about optimization. Then I realized it's about understanding bottlenecks."

Hook #2 (OUTCOME STYLE - shows specific results):
- Start with: "After [timeframe], I realized..." or "This cost me..." or "I learned..."
- Example: "I spent 6 months and $15K learning this. Now it takes 2 days."

Hook #3 (CONTRARIAN STYLE - challenges popular belief):
- Start with: "Everyone says... but the data shows...", "We all believe... which is why..."
- Example: "Everyone talks about 10x improvement. We're at 300% because the standard advice misses the real issue."

---

QUALITY RULES:
✓ Max 2 lines per hook
✓ Specific (not generic)
✓ Immediately interesting
✓ Grounded in reality
✓ Matches tone and audience
✓ Each takes a different angle

RETURN FORMAT (EXACT):
Hook #1 (Curiosity):
[hook text]

Hook #2 (Outcome):
[hook text]

Hook #3 (Contrarian):
[hook text]"""

def generate_hook_options(post: str, context: str = "", tone: str = "professional", audience: str = "technical") -> str:
    """Generate 3 different hook options for the post.
    
    Args:
        post: The LinkedIn post content to generate hooks for
        context: Optional context about the post topic
        tone: Tone of the post (used for hook style)
        audience: Target audience (used for hook style)
    
    Returns:
        String with hook options
    """
    chain = _get_hook_generator()
    result = chain.invoke({
        "topic": post[:200],  # Use first 200 chars as topic
        "context": context,
        "tone": tone,
        "audience": audience
    })
    return result.content if hasattr(result, 'content') else str(result)

# ============================================================================
# 4. CONTEXT GROUNDING CHAIN
# ============================================================================

CONTEXT_GROUNDING_PROMPT = """Your job: Ensure this LinkedIn post uses ONLY verified information from the context.

Remove any fabricated statistics, fake research claims, or unverifiable numbers.
Make it natural and informational without hallucinations.

POST:
{post}

CONTEXT (VERIFIED INFORMATION ONLY):
{context}

---

⚠️ HALLUCINATION CHECK:
1. Any number/% in post not in context? → REMOVE IT
2. "Studies show", "research indicates", "X% of people" without source? → REMOVE IT
3. Specific metrics (85%, 94% accuracy, etc.) not in context? → REMOVE IT
4. Made-up before/after comparisons? → REMOVE IT
5. Fabricated timelines/costs not in context? → REMOVE IT

✅ CORRECTION APPROACH:
1. Keep the valuable insights and frameworks
2. Replace invented numbers with qualitative explanations
3. Use context-verified information only
4. Make it informational through principles, not fake data
5. Sound natural like a professional sharing real experience
6. Maintain engagement but stay honest

---

🎯 OUTPUT INSTRUCTIONS:
Return ONLY the improved post text - nothing else.
No meta-commentary. No explanations. No labels like "HALLUCINATIONS FOUND:" or "IMPROVED VERSION:".
Just write the corrected post naturally as if you were the author.

If the post is already grounded in context with no hallucinations, return it as-is.

Write the final post now (clean output only):"""

def ground_in_context(post: str, context: str) -> str:
    """Ground post claims in provided context, remove hallucinations."""
    chain = _get_context_grounder()
    result = chain.invoke({
        "post": post,
        "context": context
    })
    return result.content if hasattr(result, 'content') else str(result)

# ============================================================================
# 5. COMPLETE QUALITY IMPROVEMENT PIPELINE
# ============================================================================

def improve_post_quality(post: str, context: str = "") -> dict:
    """
    Complete quality improvement pipeline.
    
    Returns:
        {
            'original': original post,
            'specificity_improved': post with better specificity,
            'context_grounded': post grounded in context,
            'quality_score': quality rating,
            'improvements_needed': top improvement
        }
    """
    improvements = {
        'original': post,
        'specificity_improved': enforce_specificity(post),
        'quality_score': score_post_quality(post),
    }
    
    if context:
        improvements['context_grounded'] = ground_in_context(post, context)
    
    return improvements

# ============================================================================
# INFORMATION DENSITY CHECKLIST
# ============================================================================

INFORMATION_DENSITY_CHECKLIST = """
Every LinkedIn post should have:

THE NUMBERS:
  ☐ At least 2-3 specific numbers (379, 1,200+, 6 years, 89%, $2.3M)
  ☐ At least 1 before/after metric (42% → 89%)
  ☐ At least 1 percentage improvement (40% faster, 60% cheaper)
  ☐ At least 1 timeline (6 years, 4 months, 2 days)

THE NAMES:
  ☐ Specific people/companies named (Gandhi, Nehru, Modi)
  ☐ Specific projects/products mentioned
  ☐ Real examples (not generic reference)

THE ROOT CAUSES:
  ☐ At least 2-3 root causes identified
  ☐ Each cause has evidence/proof
  ☐ Each cause has concrete example

THE HOW-TO:
  ☐ Not just WHAT, but HOW to implement
    NOT: "Create open communication"
    YES: "Dedicate 2 hours/week to listening sessions"
  ☐ Specific, actionable steps (not generic advice)
  ☐ Real example from experience
  ☐ Metrics showing it worked

THE PROOF:
  ☐ Why is writer credible? ("6 years studying", "worked with X")
  ☐ What evidence backs the claim? (numbers, case studies)
  ☐ What result can readers expect? (before/after, %)

FORBIDDEN PATTERNS:
  ❌ "I learned X" → Use "After 6 years, I discovered..."
  ❌ "It's important" → Use with specific impact
  ❌ "People should" → Use specific framework
  ❌ "Studies show" → Cite actual study

USE THIS CHECKLIST:
Run every post through these 5 categories.
If missing any, add more specifics.
Test quality immediately improves.
"""
