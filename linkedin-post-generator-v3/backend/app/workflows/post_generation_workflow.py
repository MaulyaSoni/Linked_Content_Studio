# LANGGRAPH ORCHESTRATION — HUMAN-SOUNDING POST GENERATION (v1.0.1 - fixed imports)
# Solves: Generic hooks, template structure, robotic sentences
# Stack: LangGraph + Groq + SQLAlchemy
# Location: backend/app/workflows/post_generation_workflow.py

from __future__ import annotations

import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Annotated

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.models.models import Post
from app.services.user_profile_analyzer import UserProfileAnalyzer


# ============================================================================
#  STATE — everything that flows through the graph
# ============================================================================

class PostGenerationState(TypedDict):
    # ── inputs
    user_id:            str
    topic:              str
    content_type:       str
    tone_override:      Optional[str]
    additional_context: str
    db:                 Any                 # SQLAlchemy session (not serialised)

    # ── user intelligence (built in node 1)
    user_profile:       Dict                # 9-dimension style profile
    episodic_memory:    List[Dict]          # concrete facts from past posts
    has_history:        bool                # True if user has ≥3 past posts

    # ── generation (built in nodes 2-4)
    raw_draft:          str                 # first pass — fast, free-form
    critique:           Dict                # structured feedback on raw draft
    rewritten_draft:    str                 # post after targeted rewrite

    # ── final output (built in node 5)
    final_post:         str
    hashtags:           str
    quality_score:      int
    tokens_used:        int
    node_trace:         List[str]           # which nodes ran (for debugging)


# ============================================================================
#  LLM SETUP — two models, different purposes
# ============================================================================

def _fast_llm() -> ChatGroq:
    """llama-3.1-8b — for quick passes (draft, extraction)."""
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.85,            # higher = more human-like variation
        api_key=os.getenv("GROQ_API_KEY"),
    )

def _smart_llm() -> ChatGroq:
    """llama-3.3-70b — for reasoning-heavy nodes (critique, polish)."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        api_key=os.getenv("GROQ_API_KEY"),
    )


# ============================================================================
#  NODE 1 — build_user_intelligence
#  Runs:  UserProfileAnalyzer (style) + episodic memory extraction
#  Cost:  1 LLM call if user has history, 0 if new user
# ============================================================================

async def build_user_intelligence(state: PostGenerationState) -> PostGenerationState:
    """
    Extract two things:
    1. Style profile  — HOW the user writes (tone, vocab, sentence length…)
    2. Episodic memory — WHAT they've written about (projects, opinions, wins)
    """

    db      = state["db"]
    user_id = state["user_id"]
    trace   = state.get("node_trace", [])
    trace.append("build_user_intelligence")

    # ── style profile (already implemented)
    profile = await UserProfileAnalyzer.analyze_user_profile(user_id, db)

    # ── fetch raw past posts for memory extraction
    past_posts: List[Post] = (
        db.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    has_history = len(past_posts) >= 3

    episodic_memory: List[Dict] = []

    if has_history:
        combined_text = "\n---\n".join(
            f"POST {i+1}:\n{p.content}" for i, p in enumerate(past_posts)
        )

        extraction_prompt = f"""
You are extracting structured memory from a user's LinkedIn posts.
Read all posts and extract ONLY concrete, verifiable facts.
Do NOT invent or infer. Only extract what is explicitly stated.

EXTRACT:
1. projects     — specific projects/products they built or worked on
2. companies    — companies/orgs mentioned (employer, clients, partners)
3. technologies — tools, languages, frameworks they use
4. wins         — achievements, results, metrics they shared
5. opinions     — strong opinions or beliefs they've expressed
6. industries   — domains/sectors they work in or care about
7. roles        — job titles or roles mentioned

POSTS:
{combined_text}

Return ONLY valid JSON in this exact format, nothing else:
{{
  "projects":    ["..."],
  "companies":   ["..."],
  "technologies":["..."],
  "wins":        ["..."],
  "opinions":    ["..."],
  "industries":  ["..."],
  "roles":       ["..."]
}}
"""
        try:
            resp = _fast_llm().invoke([
                SystemMessage(content="Extract structured memory from posts. Return only JSON."),
                HumanMessage(content=extraction_prompt),
            ])
            raw_json = re.sub(r"```json|```", "", resp.content).strip()
            episodic_memory = [json.loads(raw_json)]
        except Exception:
            episodic_memory = []   # graceful fallback

    return {
        **state,
        "user_profile":    profile,
        "episodic_memory": episodic_memory,
        "has_history":     has_history,
        "node_trace":      trace,
    }


# ============================================================================
#  NODE 2 — generate_raw_draft
#  Runs:  First-pass generation using full style + memory context
#  Key:   High temperature, anti-template hooks, imperfect human patterns
# ============================================================================

async def generate_raw_draft(state: PostGenerationState) -> PostGenerationState:
    """
    Generate first draft that is already anti-AI from the start.
    Injected with: memory facts, hook variety, imperfection rules.
    """

    trace = state.get("node_trace", [])
    trace.append("generate_raw_draft")

    profile  = state["user_profile"]
    memory   = state["episodic_memory"][0] if state["episodic_memory"] else {}
    tone     = state.get("tone_override") or profile.get("tone", "professional")
    topic    = state["topic"]
    ctype    = state["content_type"]
    extra    = state.get("additional_context", "")

    # ── memory injection (only what exists)
    memory_block = ""
    if memory:
        parts = []
        if memory.get("projects"):
            parts.append(f"Projects they've worked on: {', '.join(memory['projects'][:3])}")
        if memory.get("technologies"):
            parts.append(f"Technologies they use: {', '.join(memory['technologies'][:4])}")
        if memory.get("wins"):
            parts.append(f"Wins/achievements: {', '.join(memory['wins'][:2])}")
        if memory.get("opinions"):
            parts.append(f"Opinions they hold: {', '.join(memory['opinions'][:2])}")
        if memory.get("roles"):
            parts.append(f"Their role/identity: {', '.join(memory['roles'][:2])}")
        if parts:
            memory_block = "WHAT YOU KNOW ABOUT THIS USER (weave in naturally if relevant):\n" + "\n".join(parts)

    # ── hook variety (break template lock)
    hook_styles = [
        "Start mid-thought — as if continuing a conversation already in progress.",
        "Start with a sharp one-sentence opinion. No setup. Just the take.",
        "Start with a specific moment — time, place, what happened. No fluff.",
        "Start with a question that is NOT 'Have you ever…'. Be more specific.",
        "Start with a number or data point that is surprising. Then explain it.",
        "Start with a confession or admission that feels vulnerable but not dramatic.",
        "Start with a very short sentence. 3-5 words max. Then expand.",
    ]
    import random
    hook_instruction = random.choice(hook_styles)

    # ── sentence imperfection rules
    imperfection_rules = """
HUMAN WRITING RULES (follow these — they prevent AI detection):
- Use em dashes (—) occasionally instead of commas. Not every sentence.
- Vary sentence length aggressively. Some sentences = 3 words. Others = 25.
- One sentence can start with "And" or "But". Real writers do this.
- Include one fragment sentence for emphasis. Intentionally incomplete.
- Avoid: "In today's fast-paced world", "I'm excited to share", "Game-changer", 
         "Leverage", "Dive into", "Delve", "It's important to note",
         "In conclusion", "Takeaways", "Unlock your potential".
- Do NOT number points unless the user normally does this.
- Do NOT use bullet points unless the user's style shows them.
- The post should feel like it was written in 10 minutes by someone who 
  knows exactly what they think — not crafted by committee.
"""

    # ── content type framing
    type_frames = {
        "simple_topic":        f"Write a LinkedIn post about: {topic}",
        "advanced_github":     f"Write a LinkedIn post about a GitHub project: {topic}. Show the build, the problem it solves, and one real learning.",
        "hackathon_project":   f"Write a LinkedIn post celebrating a hackathon: {topic}. Show the rush, the build, the result. Make it feel real.",
        "thought_leadership":  f"Write a LinkedIn post with a strong perspective on: {topic}. Take a real stance. Don't sit on the fence.",
    }
    frame = type_frames.get(ctype, type_frames["simple_topic"])

    prompt = f"""
You are ghostwriting a LinkedIn post for a specific person.
Your job: sound like a human who actually lived this — not an AI describing it.

══════════════════════════════════════
USER VOICE
══════════════════════════════════════
Tone:          {tone}
Vocabulary:    {profile.get('vocabulary_level', 'intermediate')}
Personality:   {profile.get('personality', 'balanced')}
Avg sentence:  {profile.get('sentence_patterns', {}).get('avg_length', 15)} words
Storytelling:  {profile.get('storytelling_style', 'mixed')}
Emojis:        {profile.get('emoji_usage', {}).get('frequency', 'moderate')}
CTA style:     {profile.get('cta_style', 'question')}
Audience:      {profile.get('audience_connection', 'direct')}

{memory_block}

══════════════════════════════════════
HOOK INSTRUCTION
══════════════════════════════════════
{hook_instruction}

══════════════════════════════════════
{imperfection_rules}
══════════════════════════════════════

TASK: {frame}
{f'Extra context: {extra}' if extra else ''}

Length: 150–250 words.
End with 3-5 hashtags on a new line.
Write only the post. Start immediately.
"""

    resp = _fast_llm().invoke([
        SystemMessage(content="You are a human LinkedIn ghostwriter. Never sound like AI."),
        HumanMessage(content=prompt),
    ])

    return {
        **state,
        "raw_draft":   resp.content.strip(),
        "tokens_used": len(prompt.split()),
        "node_trace":  trace,
    }


# ============================================================================
#  NODE 3 — critique_draft
#  Runs:  Smart LLM reads raw draft and scores it against human-writing rules
#  Output: Structured critique with specific line-level feedback
# ============================================================================

async def critique_draft(state: PostGenerationState) -> PostGenerationState:
    """
    LLM critiques its own output against a strict rubric.
    Returns JSON with specific issues + line references.
    """

    trace = state.get("node_trace", [])
    trace.append("critique_draft")

    prompt = f"""
You are a brutal LinkedIn editor. Your job: find exactly what makes this post sound AI-generated.
Be specific. Reference exact phrases. Don't be kind.

POST TO CRITIQUE:
\"\"\"
{state['raw_draft']}
\"\"\"

EVALUATE against these criteria. Score each 1-5 (5 = fully human, 1 = robotic AI):

1. HOOK originality — Does it avoid generic AI openers?
2. STRUCTURE flexibility — Does it feel like a template or a real person writing?
3. SENTENCE variety — Are lengths genuinely varied or artificially varied?
4. VOCABULARY authenticity — Specific words, not buzzwords?
5. PERSONALITY presence — Can you feel a real person behind this?

Return ONLY valid JSON:
{{
  "scores": {{
    "hook":          <1-5>,
    "structure":     <1-5>,
    "sentences":     <1-5>,
    "vocabulary":    <1-5>,
    "personality":   <1-5>
  }},
  "total": <sum of scores, max 25>,
  "ai_phrases_found": ["phrase1", "phrase2"],
  "weakest_section": "quote the actual weakest line or phrase",
  "fix_instructions": [
    "Specific fix 1 with example",
    "Specific fix 2 with example"
  ],
  "needs_rewrite": <true if total < 18, else false>
}}
"""

    try:
        resp = _smart_llm().invoke([
            SystemMessage(content="You are a strict human-writing editor. Return only JSON."),
            HumanMessage(content=prompt),
        ])
        raw = re.sub(r"```json|```", "", resp.content).strip()
        critique = json.loads(raw)
    except Exception:
        # If critique fails, pass through with low score to force rewrite
        critique = {
            "scores": {"hook": 2, "structure": 2, "sentences": 3, "vocabulary": 2, "personality": 2},
            "total": 11,
            "ai_phrases_found": [],
            "weakest_section": "",
            "fix_instructions": ["Rewrite more naturally"],
            "needs_rewrite": True,
        }

    return {
        **state,
        "critique":    critique,
        "node_trace":  trace,
    }


# ============================================================================
#  ROUTING — after critique, decide: rewrite or polish directly
# ============================================================================

def route_after_critique(state: PostGenerationState) -> str:
    """If critique score < 18/25 → rewrite. Else → go straight to polish."""
    needs_rewrite = state["critique"].get("needs_rewrite", True)
    return "rewrite_draft" if needs_rewrite else "polish_and_finalise"


# ============================================================================
#  NODE 4 — rewrite_draft
#  Runs:  Only if critique score < 18. Targeted rewrite of weak parts.
# ============================================================================

async def rewrite_draft(state: PostGenerationState) -> PostGenerationState:
    """
    Targeted rewrite using critique as a surgical guide.
    Does NOT rewrite everything — only the flagged weak sections.
    """

    trace = state.get("node_trace", [])
    trace.append("rewrite_draft")

    critique      = state["critique"]
    fix_list      = "\n".join(f"- {f}" for f in critique.get("fix_instructions", []))
    ai_phrases    = ", ".join(f'"{p}"' for p in critique.get("ai_phrases_found", []))
    weak_section  = critique.get("weakest_section", "")

    prompt = f"""
You are rewriting a LinkedIn post to remove AI patterns.
Make TARGETED changes — don't rewrite everything that's working.

ORIGINAL POST:
\"\"\"
{state['raw_draft']}
\"\"\"

CRITIQUE FEEDBACK:
Weakest section: "{weak_section}"
AI phrases to remove: {ai_phrases if ai_phrases else "None specifically flagged"}
Fix instructions:
{fix_list}

RULES FOR REWRITE:
- Keep what scores well — only fix the flagged issues
- Remove every AI phrase listed above
- Fix the weakest section specifically
- Maintain the user's voice profile from the original
- Keep length 150-250 words
- Keep hashtags at the end

Write only the improved post. No commentary.
"""

    resp = _fast_llm().invoke([
        SystemMessage(content="Rewrite to sound more human. Keep what works. Fix what doesn't."),
        HumanMessage(content=prompt),
    ])

    return {
        **state,
        "rewritten_draft": resp.content.strip(),
        "node_trace":      trace,
    }


# ============================================================================
#  NODE 5 — polish_and_finalise
#  Runs:  Always last. Anti-AI polish + hashtag extraction + scoring.
# ============================================================================

async def polish_and_finalise(state: PostGenerationState) -> PostGenerationState:
    """
    Final pass:
    1. Anti-AI phrase removal (hard-coded blacklist)
    2. Structural de-templating
    3. Hashtag extraction
    4. Quality scoring
    """

    trace = state.get("node_trace", [])
    trace.append("polish_and_finalise")

    # Use whichever draft is most recent
    working_draft = state.get("rewritten_draft") or state["raw_draft"]

    # ── STEP 1: hard blacklist removal
    blacklist = [
        r"I[' ]?m excited to share",
        r"I[' ]?m thrilled to announce",
        r"game[- ]changer",
        r"\bleverage\b",
        r"\bdelve\b",
        r"\bdive into\b",
        r"it[' ]?s important to note",
        r"in today[' ]?s fast[- ]paced world",
        r"in conclusion",
        r"key takeaways?",
        r"unlock your potential",
        r"cutting[- ]edge",
        r"\bsynergy\b",
        r"\bparadigm shift\b",
        r"let[' ]?s connect",
        r"happy to announce",
        r"proud to share",
    ]

    cleaned = working_draft
    for pattern in blacklist:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

    # ── STEP 2: LLM polish pass (light — just smooth edges)
    polish_prompt = f"""
Lightly polish this LinkedIn post. 
Fix any awkward gaps left by phrase removals.
Do NOT restructure. Do NOT add new content.
Keep every sentence that already works.
The post should feel like a confident human wrote it in one sitting.

POST:
\"\"\"
{cleaned}
\"\"\"

Return only the polished post with hashtags. No commentary.
"""

    resp = _smart_llm().invoke([
        SystemMessage(content="Light polish only. Preserve human voice. Return only the post."),
        HumanMessage(content=polish_prompt),
    ])

    polished = resp.content.strip()

    # ── STEP 3: extract hashtags
    hashtag_pattern = r'#\w+'
    all_tags = re.findall(hashtag_pattern, polished)
    seen, unique_tags = set(), []
    for t in all_tags:
        if t.lower() not in seen:
            unique_tags.append(t)
            seen.add(t.lower())
    hashtags = " ".join(unique_tags[:7])

    # Remove hashtags from body
    post_body = re.sub(r'\n+#\w+.*$', '', polished, flags=re.DOTALL).strip()
    post_body = re.sub(r'#\w+', '', post_body).strip()

    # ── STEP 4: quality score
    critique_total = state.get("critique", {}).get("total", 15)
    quality_score  = _compute_quality_score(post_body, hashtags, critique_total)

    total_tokens = state.get("tokens_used", 0) + len(polish_prompt.split())

    return {
        **state,
        "final_post":   post_body,
        "hashtags":     hashtags,
        "quality_score": quality_score,
        "tokens_used":  total_tokens,
        "node_trace":   trace,
    }


# ============================================================================
#  QUALITY SCORER
# ============================================================================

def _compute_quality_score(post: str, hashtags: str, critique_total: int) -> int:
    score = 40

    # From critique (max 25 → maps to 30 points)
    score += int((critique_total / 25) * 30)

    # Word count
    wc = len(post.split())
    if 150 <= wc <= 250: score += 15
    elif 100 <= wc <= 300: score += 8

    # Hashtags
    if hashtags and len(hashtags.split()) >= 3: score += 5

    # CTA present
    if "?" in post or any(w in post.lower() for w in ["share", "comment", "let me know", "reply"]):
        score += 5

    # No blacklisted phrases remaining
    blacklist_check = ["excited to share", "game-changer", "leverage", "delve"]
    if not any(p in post.lower() for p in blacklist_check):
        score += 5

    return min(score, 100)


# ============================================================================
#  GRAPH ASSEMBLY
# ============================================================================

def build_post_generation_graph() -> Any:
    """
    Assemble the LangGraph state machine.

    Flow:
    build_user_intelligence
        ↓
    generate_raw_draft
        ↓
    critique_draft
        ↓ (conditional)
    rewrite_draft  ──┐
        ↓            │
    polish_and_finalise ←┘
        ↓
    END
    """

    graph = StateGraph(PostGenerationState)

    # Add nodes
    graph.add_node("build_user_intelligence", build_user_intelligence)
    graph.add_node("generate_raw_draft",       generate_raw_draft)
    graph.add_node("critique_draft",           critique_draft)
    graph.add_node("rewrite_draft",            rewrite_draft)
    graph.add_node("polish_and_finalise",      polish_and_finalise)

    # Entry point
    graph.set_entry_point("build_user_intelligence")

    # Linear edges
    graph.add_edge("build_user_intelligence", "generate_raw_draft")
    graph.add_edge("generate_raw_draft",      "critique_draft")

    # Conditional: rewrite if needed, skip if already good
    graph.add_conditional_edges(
        "critique_draft",
        route_after_critique,
        {
            "rewrite_draft":      "rewrite_draft",
            "polish_and_finalise":"polish_and_finalise",
        }
    )

    # Rewrite always goes to polish
    graph.add_edge("rewrite_draft", "polish_and_finalise")

    # Final node → end
    graph.add_edge("polish_and_finalise", END)

    return graph.compile()


# Singleton — compile once, reuse
_GRAPH = build_post_generation_graph()


# ============================================================================
#  PUBLIC ENTRY POINT — called from api/posts.py
# ============================================================================

async def run_post_generation_workflow(
    user_id:            str,
    topic:              str,
    db:                 Session,
    content_type:       str = "simple_topic",
    tone_override:      Optional[str] = None,
    additional_context: str = "",
) -> Dict:
    """
    Run the full LangGraph workflow.
    Returns dict compatible with existing CompatGenerateResponse schema.
    """

    initial_state: PostGenerationState = {
        "user_id":            user_id,
        "topic":              topic,
        "content_type":       content_type,
        "tone_override":      tone_override,
        "additional_context": additional_context,
        "db":                 db,
        "user_profile":       {},
        "episodic_memory":    [],
        "has_history":        False,
        "raw_draft":          "",
        "critique":           {},
        "rewritten_draft":    "",
        "final_post":         "",
        "hashtags":           "",
        "quality_score":      0,
        "tokens_used":        0,
        "node_trace":         [],
    }

    try:
        final_state = await _GRAPH.ainvoke(initial_state)

        return {
            "success":              True,
            "post":                 final_state["final_post"],
            "hashtags":             final_state["hashtags"],
            "quality_score":        final_state["quality_score"],
            "tokens_used":          final_state["tokens_used"],
            "mode_used":            "langgraph_orchestrated",
            "personalization_level":"advanced",
            "node_trace":           final_state["node_trace"],
            "has_history":          final_state["has_history"],
            "profile_summary": {
                "tone":        final_state["user_profile"].get("tone"),
                "personality": final_state["user_profile"].get("personality"),
                "post_count":  final_state["user_profile"].get("post_count", 0),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error":   str(e),
            "post":    None,
            "hashtags": None,
            "quality_score": 0,
            "tokens_used":   0,
        }
