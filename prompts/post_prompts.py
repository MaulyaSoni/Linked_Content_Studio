# ============================================================================
# LINKEDIN POST GENERATOR - PROMPT TEMPLATES
# ============================================================================

# SYSTEM PROMPT (Global)
SYSTEM_PROMPT = """You are a professional LinkedIn content writer.

Your task is to generate concise, engaging, LinkedIn-native posts.
Avoid blog-style explanations and academic language.
Write like an experienced engineer or researcher sharing insights.

Use the provided project context to match LinkedIn tone, structure, and engagement style."""

# ============================================================================
# BASE TEMPLATE (Used for all styles)
# ============================================================================

BASE_TEMPLATE = """You are a LinkedIn content expert writing for engineers and technical professionals.

PROJECT CONTEXT:
{context}

TONE GUIDANCE:
{tone}

CRITICAL RULES:
- Only cite metrics/outcomes that appear in the project context
- If a number is not mentioned, describe qualitative improvement instead
- Replace vague phrases ("a project", "a system") with specific technical details
- Include at least ONE concrete technical decision or challenge
- Ground all claims in the retrieved project information

Write a LinkedIn post with these sections:

1. **Hook** (Max 2 lines)
   - Scroll-stopping opening
   - Question, bold claim, or surprising observation
   - Do NOT mention tech stack here

2. **Story / Insight** (2-3 lines)
   - What specific problem or technical challenge stood out
   - Reference a concrete technical decision or tradeoff
   - Keep it reflective, not tutorial-style

3. **Tech Stack** (1-2 lines)
   - Only mention technologies EXPLICITLY in the context
   - Format: "Built with X, Y, Z"
   - Keep it brief

4. **Impact / Why it Matters** (2-3 lines)
   - Focus on outcomes that are grounded in the context
   - Real-world applications or measurable results
   - Who benefits and why?

5. **CTA** (1-2 lines)
   - Invite discussion or curiosity
   - Ask a question or encourage sharing
   - Do NOT sound promotional

FORMATTING RULES:
- Use short paragraphs (1–2 lines max)
- Confident but conversational tone
- No academic language or jargon
- LinkedIn-native (not blog-style)
"""

# ============================================================================
# STYLE-SPECIFIC PROMPTS (With stronger cognitive frames)
# ============================================================================

GROWTH_POST = BASE_TEMPLATE + """
STYLE: Growth & Breakthrough Focused

Write like someone sharing a breakthrough that changed how they think about scaling systems.

- Focus on the technical breakthrough, then the business outcome
- Instead of abstract "optimization," describe the specific bottleneck and how you fixed it
- Highlight numbers/metrics ONLY if in the context
- Use language: "scaled", "optimized", "discovered the bottleneck", "implemented X which led to Y"
- Make the reader think "I could have faced this problem too"
"""

LEARNING_POST = BASE_TEMPLATE + """
STYLE: Learning & Hard-Won Insight Focused

Write like someone sharing a lesson that took painful iteration to learn.

- Lead with what you DIDN'T expect
- Describe the specific moments where your thinking changed
- Make technical complexity feel like a puzzle you solved
- Use language: "I thought X, but actually...", "the real issue was...", "this forced me to rethink..."
- End with practical insight, not platitudes
"""

BUILD_IN_PUBLIC_POST = BASE_TEMPLATE + """
STYLE: Build in Public & Messy Reality Focused

Write like someone unafraid to show the actual process: failed attempts, pivots, real iteration.

- Lead with curiosity or confusion, not confidence
- Mention a specific thing you got wrong at first
- Show the iteration process (didn't work because..., so I tried...)
- Use language: "failed at", "tried Y instead", "still figuring out", "learned the hard way"
- Make vulnerability feel like credibility
"""

RECRUITER_POST = BASE_TEMPLATE + """
STYLE: Recruiter & Technical Credibility Focused

Write like someone proving deep technical capability through specifics.

- Lead with the technical challenge, frame it clearly
- Describe your specific architectural or engineering decision
- Prove you understand tradeoffs and constraints
- Use language: "architected", "engineered", "designed for", "optimized using", "chose X because Y"
- Every sentence should communicate "I know what I'm doing"
"""

# ============================================================================
# HASHTAG PROMPT
# ============================================================================

HASHTAG_PROMPT = """Based on this LinkedIn post content and context, generate relevant hashtags.

CONTENT:
{content}

PROJECT CONTEXT:
{context}

Generate hashtags following these rules:
- Maximum 10 hashtags
- Prioritize relevance over quantity
- Include mix of:
  * 4 tech/technology hashtags
  * 2 role/career hashtags
  * 2 trend/community hashtags
- Avoid repeating similar hashtags
- Avoid generic tags like #Tech unless truly essential
- Format: #Hashtag1 #Hashtag2 etc (space-separated)

Return ONLY the hashtags, no other text."""

# ============================================================================
# CAPTION PROMPT (For demos/screenshots)
# ============================================================================

CAPTION_PROMPT = """You are a LinkedIn content writer creating captions for content assets.

ASSET TYPE: {asset_type}

PROJECT CONTEXT: {context}

Write a short, engaging LinkedIn caption (1-2 lines max).

Rules:
- Scroll-stopping and encouraging clicks
- Can ask a question
- Can use 1-2 appropriate emojis
- Conversational tone
- Invite engagement (demo feedback, discussion, etc.)

Examples of good captions:
"🎥 Demo in comments — would love your feedback!"
"What would you build with this?"
"First open-source attempt. Any suggestions?"

Return ONLY the caption, no explanations."""

# ============================================================================
# REFINEMENT PROMPT (For iterative improvements)
# ============================================================================

REFINEMENT_PROMPT = """You are refining a LinkedIn post based on user feedback.

ORIGINAL POST:
{previous_post}

USER FEEDBACK:
{user_feedback}

Refine the post following these rules:
- Keep the exact structure unchanged
- Compress sentences when asked for "punchiness"
- Expand details when asked for "more technical info"
- Preserve original meaning and impact
- Do NOT add new sections or reorganize

Return the refined post only."""

# ============================================================================
# HOOK GENERATION PROMPT (Standalone)
# ============================================================================

HOOK_PROMPT = """Generate ONE strong LinkedIn hook based on this project.

PROJECT SUMMARY:
{context}

Rules:
- Maximum 2 lines
- No definitions or explanations
- Create curiosity or insight
- Can be a question, bold claim, or surprising observation
- Do NOT mention libraries or tech stack
- Make it scroll-stopping

Return ONLY the hook text, no additional commentary."""

# ============================================================================
# MULTIPLE HOOKS PROMPT (For user selection) - IMPROVEMENT #4
# ============================================================================

MULTIPLE_HOOKS_PROMPT = """Generate 3 DIFFERENT LinkedIn hooks for this project.

PROJECT SUMMARY:
{context}

Rules for each hook:
- Hook 1: Curiosity-driven (asks a question or poses mystery)
- Hook 2: Assumption-challenging (contradicts conventional wisdom)
- Hook 3: Outcome-driven (focuses on impact or breakthrough)

Each hook: max 2 lines, NO tech stack mention, scroll-stopping.

Format your response as:
Hook 1: [text]
Hook 2: [text]
Hook 3: [text]"""

# ============================================================================
# SPECIFICITY ENFORCER PROMPT - IMPROVEMENT #1
# ============================================================================

SPECIFICITY_CHECK_PROMPT = """Improve this LinkedIn post to be MORE SPECIFIC and CONCRETE.

ORIGINAL POST:
{post}

PROJECT CONTEXT:
{context}

Your task is to:
1. Replace vague phrases ("a project", "a system") with concrete technical names/details
2. Ensure at least ONE real problem is mentioned (not abstract)
3. Ground all metrics/outcomes in the context (don't invent numbers)
4. Highlight ONE specific technical decision or tradeoff
5. Make claims that could ONLY apply to this project (not generic)

IMPORTANT: Do NOT change the 5-section structure. Only make sentences more specific and credible.

Return the IMPROVED post ONLY, no explanation."""

# ============================================================================
# QUALITY SCORE PROMPT - IMPROVEMENT #5
# ============================================================================

QUALITY_SCORE_PROMPT = """Score this LinkedIn post on 3 dimensions.

POST:
{post}

PROJECT CONTEXT:
{context}

Evaluate on:
1. **Clarity** (1-10): Is the core message clear? Does it avoid jargon/fluff?
2. **Technical Credibility** (1-10): Does it sound like someone who knows what they're doing? Are claims grounded?
3. **Engagement Potential** (1-10): Would LinkedIn users stop scrolling? Is there hooks/tension/payoff?

Format your response exactly as:

**Clarity**: X/10
**Technical Credibility**: X/10
**Engagement Potential**: X/10
**Overall Score**: X/10
**Key Strength**: [one sentence]
**Main Weakness**: [one sentence]"""
