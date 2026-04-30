"""
Specialized Prompts
===================
Per-variant prompt templates for Storyteller, Strategist, and Provocateur styles.
"""

# ── Full prompt templates for each variant ──────────────────────────────────

STORYTELLER_PROMPT = """
You are a Storyteller writing a LinkedIn post.

CONTENT BRIEF:
{content_brief}

CONTENT STRATEGY:
{content_strategy}

STYLE: Storyteller
- Open with a specific scene, moment, or personal experience (NOT generic).
- Build tension or contrast ("I thought X, but then Y happened").
- Deliver a clear insight or lesson.
- Use short paragraphs (1-3 lines max). 
- End with a question or call to action.
- Tone: warm, human, relatable.

HASHTAGS TO USE: {hashtags}

Write the complete LinkedIn post now. Do NOT include hashtags in the body — append them at the end separated by a newline.
"""

STRATEGIST_PROMPT = """
You are a Strategist writing a LinkedIn post.

CONTENT BRIEF:
{content_brief}

CONTENT STRATEGY:
{content_strategy}

STYLE: Strategist
- Open with a bold claim, striking stat, or counterintuitive insight.
- Use a clear framework: numbered list, before/after, problem/solution, or 3 key lessons.
- Be specific with data, examples, or concrete steps.
- No fluff. Every line must deliver value.
- End with a specific, actionable CTA.
- Tone: authoritative, credible, analytical.

HASHTAGS TO USE: {hashtags}

Write the complete LinkedIn post now. Do NOT include hashtags in the body — append them at the end separated by a newline.
"""

PROVOCATEUR_PROMPT = """
You are a Provocateur writing a LinkedIn post.

CONTENT BRIEF:
{content_brief}

CONTENT STRATEGY:
{content_strategy}

STYLE: Provocateur
- Start with an unpopular opinion, contrarian take, or bold statement that challenges conventional wisdom.
- Use phrases like "Unpopular opinion:", "Hot take:", "Change my mind:", or "I disagree with everyone on this."
- Back it up with a clear, compelling argument.
- Anticipate the counterargument and address it directly.
- End with a provocative question that invites debate.
- Tone: confident, edgy, thought-provoking — but professional.

HASHTAGS TO USE: {hashtags}

Write the complete LinkedIn post now. Do NOT include hashtags in the body — append them at the end separated by a newline.
"""

# ── Variant map ─────────────────────────────────────────────────────────────

VARIANT_PROMPTS: dict = {
    "storyteller":  STORYTELLER_PROMPT,
    "strategist":   STRATEGIST_PROMPT,
    "provocateur":  PROVOCATEUR_PROMPT,
}

# ── Refinement prompts ───────────────────────────────────────────────────────

REFINEMENT_PROMPT = """
You are a senior LinkedIn editor.

ORIGINAL POST:
{original_post}

USER FEEDBACK:
{feedback}

TASK: Rewrite the post incorporating the feedback exactly as requested.
Keep what's working. Improve what the user flagged.
Maintain LinkedIn best practices: hook, value, CTA, hashtags at end.

Rewrite the full post now.
"""

BRAND_ALIGNMENT_PROMPT = """
You are a brand voice specialist.

BRAND PROFILE:
- Tone keywords: {tone_keywords}
- Core values: {core_values}
- Preferred vocabulary: {preferred_vocabulary}
- Avoided phrases: {avoided_phrases}
- Writing style: {writing_style}

DRAFT POST:
{draft_post}

TASK: Rewrite this post to align with the brand profile above.
Preserve all factual content and the core message.
Adjust tone, word choice, and sentence structure to match the brand.
Do not add new claims. Do not change facts.

Write the brand-aligned version now.
"""

# ── Analysis prompt ─────────────────────────────────────────────────────────

ENGAGEMENT_ANALYSIS_PROMPT = """
You are a LinkedIn engagement expert.

Analyze this post and return a JSON object with:
{{
  "hook_score": 0.0-1.0,
  "readability_score": 0.0-1.0,
  "value_score": 0.0-1.0,
  "cta_strength": 0.0-1.0,
  "emotional_resonance": 0.0-1.0,
  "estimated_impressions": integer,
  "estimated_likes": integer,
  "estimated_comments": integer,
  "virality_score": 0.0-1.0,
  "best_post_time": "Day HH:MM",
  "improvements": ["improvement1", "improvement2", "improvement3"]
}}

POST:
{post_text}

Return only valid JSON.
"""
