# LinkedIn Post Generator — Complete System Documentation

> A comprehensive technical guide covering the full pipeline: from user input, through all 6 AI agents, LLM integration, to automatic LinkedIn publishing.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [The LLM Engine — How AI Generates Content](#4-the-llm-engine--how-ai-generates-content)
5. [The 6-Agent Pipeline — Detailed Breakdown](#5-the-6-agent-pipeline--detailed-breakdown)
   - [Agent 1 — InputProcessorAgent](#agent-1--inputprocessoragent)
   - [Agent 2 — ResearchAgent](#agent-2--researchagent)
   - [Agent 3 — ContentIntelligenceAgent](#agent-3--contentintelligenceagent)
   - [Agent 4 — GenerationAgent](#agent-4--generationagent)
   - [Agent 5 — BrandVoiceAgent](#agent-5--brandvoiceagent)
   - [Agent 6 — OptimizationAgent](#agent-6--optimizationagent)
6. [Agent Orchestrator — How Agents Talk to Each Other](#6-agent-orchestrator--how-agents-talk-to-each-other)
7. [LinkedIn Auto-Posting — Complete Flow](#7-linkedin-auto-posting--complete-flow)
8. [LinkedIn Posts API Integration](#8-linkedin-posts-api-integration)
9. [UI Architecture](#9-ui-architecture)
10. [Data Models](#10-data-models)
11. [Configuration & Environment Variables](#11-configuration--environment-variables)
12. [End-to-End Flow Diagram](#12-end-to-end-flow-diagram)

---

## 1. System Overview

The LinkedIn Post Generator is a **multi-agent AI application** built with Streamlit. It accepts multi-modal input (text, images, PDFs, URLs), runs it through a sequential pipeline of 6 specialized AI agents powered by **Groq's LLaMA models**, generates 3 high-quality LinkedIn post variants, and allows one-click (or scheduled) publishing directly to LinkedIn via the LinkedIn REST API v2.

**Key capabilities:**
- Multi-modal input: text, images, documents (PDF/DOCX), web URLs
- 6-agent AI pipeline for deep content intelligence
- 3 post variants per run: Storyteller, Strategist, Provocateur
- Brand voice matching using the user's past posts
- Engagement prediction and sentiment analysis
- One-click LinkedIn posting or scheduled publishing
- Real-time agent progress dashboard in the UI

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| **UI Framework** | Streamlit |
| **LLM Provider** | Groq (via `langchain-groq`) |
| **LLM Model** | LLaMA 3 (configurable in `GenerationConfig`) |
| **Agent Framework** | Custom `BaseAgent` class (no external agent framework) |
| **LinkedIn API** | LinkedIn REST API v2 (`/rest/posts`) |
| **Auth** | OAuth 2.0 Bearer Token |
| **Environment** | Python `.env` via `python-dotenv` |
| **HTTP Client** | `requests` library |

---

## 3. Project Structure

```
app.py                        ← Streamlit entry point
agents/
  agent_orchestrator.py       ← Runs all 6 agents in sequence
  input_processor_agent.py    ← Agent 1: parse multi-modal input
  research_agent.py           ← Agent 2: trends & market intel
  content_intelligence_agent.py ← Agent 3: strategy & angles
  generation_agent.py         ← Agent 4: write 3 post variants
  brand_voice_agent.py        ← Agent 5: brand DNA matching
  optimization_agent.py       ← Agent 6: engagement prediction
  linkedin_posting_agent.py   ← Post-pipeline: publishes to LinkedIn
  base_agent.py               ← Shared BaseAgent class
core/
  llm.py                      ← Groq LLM provider wrapper
  models.py                   ← All dataclasses & enums
  generator.py                ← Simple/Advanced generation modes
tools/
  linkedin_poster.py          ← Low-level LinkedIn API calls
  trend_analyzer.py           ← Hashtag & trend research
  brand_analyzer.py           ← Brand DNA analysis
  engagement_predictor.py     ← Virality score prediction
  sentiment_analyzer.py       ← Tone/sentiment analysis
  vision_analyzer.py          ← Image content extraction (LLM vision)
  document_processor.py       ← PDF/DOCX text extraction
  web_scraper.py              ← URL scraping & summarization
ui/
  components.py               ← Simple mode UI components
  agent_dashboard.py          ← Agentic Studio dashboard
  multi_modal_input.py        ← File/URL upload UI
  styles.py                   ← CSS & page config
```

---

## 4. The LLM Engine — How AI Generates Content

**File:** `core/llm.py`

All AI text generation flows through the `LLMProvider` class, which wraps **Groq's LLaMA model** via LangChain.

### Initialization

```python
self.llm = ChatGroq(
    model=self.config.model_name,     # e.g. "llama3-70b-8192"
    api_key=self.api_key,             # from GROQ_API_KEY env var
    temperature=self.config.temperature,  # 0.7 for creative, 0.0 for deterministic
    max_tokens=self.config.max_tokens,
)
```

### How a generation call works

Every agent that needs LLM reasoning calls `LLMProvider.generate()`:

```
Agent calls self.think(prompt, system_prompt)
    ↓
LLMProvider.generate(prompt, system_prompt)
    ↓
Messages are constructed:
  [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    ↓
self.llm.invoke(messages)  ← single Groq API call
    ↓
Returns LLMResult(content, tokens_used, success)
```

### Two temperature modes

| Mode | Temperature | Used for |
|---|---|---|
| **Creative** (`get_llm()`) | `0.7` | Post generation, content strategy |
| **Deterministic** (`get_llm_deterministic()`) | `0.0` | Quality scoring, brand consistency checks |

### Error handling

If the Groq API call fails for any reason (rate limit, network error, etc.), `LLMProvider.generate()` returns `LLMResult(success=False)` and every agent gracefully falls back to a **hardcoded template** — the app never crashes.

---

## 5. The 6-Agent Pipeline — Detailed Breakdown

The pipeline is defined in `agent_orchestrator.py` as an ordered list:

```python
PIPELINE = [
    ("InputProcessor",       InputProcessorAgent,       weight=0.10),
    ("Research",             ResearchAgent,             weight=0.20),
    ("ContentIntelligence",  ContentIntelligenceAgent,  weight=0.30),
    ("Generation",           GenerationAgent,           weight=0.55),
    ("BrandVoice",           BrandVoiceAgent,           weight=0.75),
    ("Optimization",         OptimizationAgent,         weight=0.95),
]
```

Each agent:
1. Receives a shared `context` dictionary (accumulated from all previous agents)
2. Runs its specialized logic (with or without LLM calls)
3. Returns an `AgentResult` with `output`, `summary`, and `context_passed`
4. Its output is **merged back into the shared context** for the next agent

---

### Agent 1 — InputProcessorAgent

**File:** `agents/input_processor_agent.py`  
**Position:** First in pipeline  
**Progress weight:** 10%

#### Purpose
Acts as the **data ingestion layer**. It accepts every supported input modality and converts them into a single unified text block that all subsequent agents can work with.

#### Supported Input Types

| Input | Tool Used | What It Does |
|---|---|---|
| Raw text / topic | Direct processing | Wraps in `[TEXT INPUT]` block |
| Images (JPG, PNG) | `VisionAnalyzer` | Uses LLM vision to extract description, themes, and content angles from the image |
| Documents (PDF, DOCX) | `DocumentProcessor` | Extracts text, summarizes key points |
| URLs | `WebScraper` | Scrapes page, extracts title, description, and key points |

#### LLM Call
After collecting all content pieces, it calls the LLM with a **content synthesis prompt**:

```
From the following multi-modal content, extract:
1. Core topic / main theme
2. Key messages (up to 5)
3. Target audience
4. Best LinkedIn post angle

Content: [combined extracted content, max 3000 chars]
```

System prompt: `"You are an expert content strategist."`

#### Output passed to next agent
```python
{
    "combined_content": str,   # full raw extraction from all sources
    "synthesis":        str,   # LLM-generated single coherent summary
    "content_types":    list,  # e.g. ["text", "image", "url"]
    "raw_text":         str,   # original user text
    "themes":           list,  # extracted theme keywords
    "image_count":      int,
    "doc_count":        int,
    "url_count":        int,
}
```

---

### Agent 2 — ResearchAgent

**File:** `agents/research_agent.py`  
**Position:** Second in pipeline  
**Progress weight:** 20%

#### Purpose
Acts as the **market intelligence engine**. It researches what content is currently trending on LinkedIn around the user's topic, identifies hashtags, and finds content gaps and competitive opportunities.

#### Core Tool: `TrendAnalyzer`
Analyzes the topic for:
- `trending_hashtags` — list of relevant hashtags with traction
- `related_topics` — adjacent topics the audience cares about
- `content_opportunities` — gaps in current LinkedIn content
- `recommended_tone` — e.g. "educational", "inspiring", "provocative"
- `best_content_type` — e.g. "list", "story", "data-driven"
- `trend_score` — 0.0–1.0 relevance/traction score
- `audience_interests` — what the target audience is reading

#### LLM Calls (2 separate calls)

**Call 1 — Competitor Insights:**
```
Topic: [user topic]
What content about this topic performs best on LinkedIn right now?
Give 3 insights about what the audience currently craves.
```
System prompt: `"You are a LinkedIn content market researcher."`

**Call 2 — Content Gaps:**
```
Topic: [user topic]
What angles or perspectives are under-represented on LinkedIn for this topic?
Give 3 content gap opportunities.
```
System prompt: `"You are a content strategy expert."`

#### Output passed to next agent
```python
{
    "topic":               str,
    "trending_hashtags":   list,   # e.g. ["#AI", "#Innovation", "#Leadership"]
    "related_topics":      list,
    "content_opportunities": list,
    "recommended_tone":    str,    # e.g. "professional"
    "best_content_type":   str,    # e.g. "educational"
    "trend_score":         float,  # 0.0 - 1.0
    "competitor_insights": str,    # LLM output
    "content_gaps":        str,    # LLM output
    "audience_interests":  list,
}
```

---

### Agent 3 — ContentIntelligenceAgent

**File:** `agents/content_intelligence_agent.py`  
**Position:** Third in pipeline  
**Progress weight:** 30%

#### Purpose
Acts as the **senior content strategist**. It takes the raw content + research and builds a full strategic blueprint: what to say, to whom, how to say it, and in which 3 different angles.

#### LLM Call (1 structured call)
This is the most complex prompt in the pipeline — it asks the LLM to produce a structured response with 8 labeled fields:

```
Build a LinkedIn content strategy for this topic.

CONTENT: [synthesis, max 2000 chars]
MARKET INTELLIGENCE: [competitor insights]
CONTENT GAPS: [gap opportunities]
Tone preference: [tone] | Audience: [audience]

Return:
KEY_MESSAGE: [the single most important thing to communicate]
TARGET_AUDIENCE: [specific audience description]
EMOTIONAL_HOOK: [the emotional angle to lead with]
ANGLE_1_STORYTELLER: [narrative-driven post angle in 2 sentences]
ANGLE_2_STRATEGIST: [data/insight-driven angle in 2 sentences]
ANGLE_3_PROVOCATEUR: [contrarian/bold angle in 2 sentences]
CONTENT_PILLARS: [3 content pillars, comma-separated]
CALL_TO_ACTION: [best CTA for this content]
```

System prompt: `"You are a senior LinkedIn content strategist."`

The response is parsed line-by-line with `_parse_strategy()`.

#### The 3 Post Angles Defined Here
| Angle | Description |
|---|---|
| `storyteller` | Narrative-driven, personal hook, emotional journey, ends with a question |
| `strategist` | Data-driven, framework-based, structured list, insight-led |
| `provocateur` | Contrarian, bold opinion, challenges conventional wisdom, invites debate |

#### Output passed to next agent
```python
{
    "strategy": {
        "key_message":      str,
        "target_audience":  str,
        "emotional_hook":   str,
        "content_pillars":  list,
        "call_to_action":   str,
    },
    "angles": {
        "storyteller":  str,   # specific angle instruction for GenerationAgent
        "strategist":   str,
        "provocateur":  str,
    },
    "tone":         str,
    "audience":     str,
    "content_type": str,
    "hashtags":     str,   # carried forward from ResearchAgent
    "synthesis":    str,
}
```

---

### Agent 4 — GenerationAgent

**File:** `agents/generation_agent.py`  
**Position:** Fourth in pipeline  
**Progress weight:** 55%

#### Purpose
The **creative writer** of the system. It takes the strategy blueprint and generates 3 distinct, ready-to-post LinkedIn post variants. This is where the actual final content is written by the LLM.

#### How it generates 3 variants
It loops over `["storyteller", "strategist", "provocateur"]` and for each makes a separate LLM call with a **variant-specific system prompt**:

**Storyteller system prompt:**
```
You are a master LinkedIn storyteller. Write narrative-driven posts that open
with a personal hook, build tension, deliver insight, and end with a genuine
question. Sound like a real human, not a content machine.
```

**Strategist system prompt:**
```
You are a sharp LinkedIn strategist. Write data-driven, insight-led posts that
open with a bold fact or framework, deliver structured value (lists/steps),
and close with a discussion-provoking question.
```

**Provocateur system prompt:**
```
You are a bold LinkedIn thought leader. Write contrarian posts that challenge
conventional wisdom, open with an opinion that makes people stop scrolling,
argue your position with evidence, and invite debate.
```

#### Per-variant generation prompt
```
Write a LinkedIn post using the '[variant_type]' style.

CONTENT TO USE: [combined content, max 2500 chars]
POST ANGLE: [angle from ContentIntelligenceAgent]
KEY MESSAGE: [key_message from strategy]
TONE: [tone preference]
TARGET AUDIENCE: [audience]
CALL TO ACTION: [CTA from strategy]

RULES:
- Max 1500 characters (ideal LinkedIn length)
- No fake statistics unless from the source content
- End with a genuine question
- Use line breaks for mobile readability
- DO NOT include hashtags (handled separately)
- Return ONLY the post text, no labels or explanations
```

#### Fallback (if LLM unavailable)
If the LLM is not available, each variant falls back to a hardcoded template populated with the topic string. The app still produces usable output.

#### Output passed to next agent
```python
{
    "variants": {
        "storyteller":  str,   # full post text, ~300-1500 chars
        "strategist":   str,
        "provocateur":  str,
    },
    "hashtags": str,
    "strategy": dict,
    "tone":     str,
    "audience": str,
}
```

---

### Agent 5 — BrandVoiceAgent

**File:** `agents/brand_voice_agent.py`  
**Position:** Fifth in pipeline  
**Progress weight:** 75%

#### Purpose
The **brand guardian**. It checks each generated variant against the user's established brand voice (built from their past LinkedIn posts) and personalizes posts that deviate from it. If no past posts are available, it passes the variants through unchanged with a default 0.7 consistency score.

#### Core Tool: `BrandAnalyzer`
- `analyze_past_posts(past_posts)` — Builds a `BrandProfile` from the user's historical posts, capturing: dominant tone, emoji usage, storytelling style, list usage, vocabulary patterns, sentence length
- `check_consistency(post_text, profile)` — Scores a new post against the profile (0.0–1.0) and identifies aligned elements, deviations, and specific suggestions

#### Decision Logic
```
For each variant:
  1. If brand profile exists → run consistency check
  2. If consistency_score < 0.7 AND LLM available → personalize the post
  3. If consistency_score >= 0.7 → pass through unchanged
  4. If no brand profile → pass through with note to add past posts
```

#### LLM Call (triggered only when consistency < 0.7)
```
Rewrite this LinkedIn post to better match this brand voice:
BRAND VOICE: [voice description — tone, emoji usage, storytelling style, list usage]
ORIGINAL POST: [the generated variant]

Rules:
- Keep the core message identical
- Only adjust tone/style to match brand
- No fake statistics
- Return ONLY the rewritten post
```

System prompt: `"You are a brand voice specialist."`

#### Output passed to next agent
```python
{
    "variants": dict,           # same keys, potentially personalized text
    "hashtags": str,
    "brand_feedback": {
        "storyteller": {
            "consistency_score": float,   # 0.0 - 1.0
            "aligned":           list,    # what's working
            "deviations":        list,    # what doesn't match brand
            "suggestions":       list,    # how to improve
            "brand_aligned":     bool,
        },
        "strategist":  { ... },
        "provocateur": { ... },
    },
    "brand_consistency_avg": float,
    "strategy": dict,
}
```

---

### Agent 6 — OptimizationAgent

**File:** `agents/optimization_agent.py`  
**Position:** Sixth (final) in pipeline  
**Progress weight:** 95%

#### Purpose
The **performance optimizer and analyst**. It predicts engagement metrics for each variant, analyzes sentiment, ranks variants by virality score, optimizes the final hashtag set, and produces actionable recommendations. It decides which variant is the "best pick."

#### Core Tools Used

**`EngagementPredictor`** — Predicts per-variant:
- `estimated_impressions` — e.g. "2,000–10,000"
- `estimated_likes` — e.g. "50–200"
- `estimated_comments` — e.g. "10–40"
- `engagement_rate` — e.g. "3–5%"
- `virality_score` — 0.0–1.0 composite score
- `predicted_reach_tier` — "low" / "moderate" / "high" / "viral"
- `best_posting_times` — e.g. ["8:00 AM", "12:00 PM"]
- `best_posting_days` — e.g. ["Tuesday", "Wednesday", "Thursday"]
- `optimization_tips` — list of actionable improvement suggestions

**`SentimentAnalyzer`** — Analyzes per-variant:
- `emotional_tone` — e.g. "inspirational", "analytical", "provocative"
- `overall_sentiment` — "positive" / "neutral" / "negative"
- `audience_perception` — how the audience will likely receive the post
- `improvements` — suggestions to improve emotional impact

#### Best Variant Selection
The agent tracks the `virality_score` across all 3 variants and selects the one with the **highest score** as `best_variant`. This recommendation is shown prominently in the UI.

#### Hashtag Optimization (`_optimize_hashtags`)
```
1. Start with hashtags from ResearchAgent
2. Add up to 2 strategy-based pillar hashtags (if not already present)
3. Trim to a maximum of 8 hashtags (LinkedIn optimal range)
```

#### Final Recommendations Built
```python
[
    "🏆 Use the 'Storyteller' variant for best expected engagement",
    "⏰ Best time to post: Tuesday–Thursday, 8–10 AM",
    # + up to 3 optimization tips from EngagementPredictor
    "💬 CTA: [call to action from strategy]"
]
```

#### Final output (OrchestratorResult)
This is the complete output handed back to the UI:
```python
OrchestratorResult(
    success=True,
    variants={
        "storyteller":  str,
        "strategist":   str,
        "provocateur":  str,
    },
    hashtags=str,                  # 5–8 optimized hashtags
    strategy=dict,                 # key_message, CTA, pillars, etc.
    research=dict,                 # trending hashtags, market intel
    brand_feedback=dict,           # per-variant brand consistency
    optimization=dict,             # per-variant engagement predictions
    overall_recommendations=list,  # actionable next steps
    best_variant=str,              # "storyteller" / "strategist" / "provocateur"
    total_time=float,              # seconds for full pipeline
    agents_run=list,               # names of agents that succeeded
)
```

---

## 6. Agent Orchestrator — How Agents Talk to Each Other

**File:** `agents/agent_orchestrator.py`

The orchestrator uses a **single shared context dictionary** pattern — not a message bus or event system.

```python
def execute_workflow(self, user_input: Dict) -> OrchestratorResult:
    context = dict(user_input)       # starts as the raw user form input

    for label, _, progress in PIPELINE:
        agent = self.agents[label]
        result = agent.run(context)   # agent reads from context

        if result.success:
            # Merge agent output BACK into context for the next agent
            context.update(result.context_passed)
            for k, v in result.output.items():
                if k not in context or not context[k]:
                    context[k] = v
```

**Context grows as agents run:**

```
After InputProcessor:  context has synthesis, combined_content, themes
After Research:        context now also has trending_hashtags, recommended_tone, market_intelligence
After ContentIntel:    context now also has strategy, angles
After Generation:      context now also has variants
After BrandVoice:      context.variants may be updated + brand_feedback added
After Optimization:    context now also has optimization, best_variant, overall_recommendations
```

**Resilient by design:** If any agent fails (exception or `result.success=False`), the orchestrator logs a warning and **continues to the next agent**. The pipeline never fully aborts. The next agent works with whatever context has been built so far.

**Real-time UI updates:** An optional `status_callback` function is called before and after each agent, emitting a `WorkflowStatus` object with `agent_name`, `status`, `message`, and `progress` (0.0–1.0). The Streamlit dashboard uses this to animate the agent progress cards live.

---

## 7. LinkedIn Auto-Posting — Complete Flow

> **Important:** Posting is NOT fully automatic. The 6-agent pipeline generates the content. A human reviews, then clicks "Post Now" or "Schedule" in the UI. The agent then calls the LinkedIn API.

### The two UI entry points

**Entry Point A — Agentic Studio (agent_dashboard.py)**  
Each of the 3 variant cards has individual action buttons:
- `📤 Post Now` → immediately publishes that specific variant
- `⏰ Schedule` → shows a date/time picker, then schedules

**Entry Point B — Simple Mode (components.py)**  
A single `📤 Post Now` button posts the currently selected/edited post text.

### Step-by-step posting flow

```
1. User clicks "📤 Post Now" on a variant card
         ↓
2. UI spawns a st.spinner("Posting to LinkedIn…")
         ↓
3. LinkedInPoster() is instantiated
   (reads LINKEDIN_ACCESS_TOKEN + LINKEDIN_USER_ID from .env)
         ↓
4. poster.post_to_linkedin(post_content=post_text, hashtags=response.hashtags)
         ↓
5. Full content assembled: content = post_text + "\n\n" + hashtags
         ↓
6. API payload built (see Section 8)
         ↓
7. HTTP POST to https://api.linkedin.com/rest/posts
         ↓
8. LinkedIn returns HTTP 201 + "x-restli-id" header → post_id extracted
         ↓
9. post_url = "https://www.linkedin.com/feed/update/{post_id}"
         ↓
10. UI shows: ✅ Posted! [View Post](post_url)
```

### Scheduling flow

```
1. User picks a future date + time in the UI
         ↓
2. ISO datetime string constructed: "2026-03-01T09:00:00"
         ↓
3. poster.schedule_post(post_content, scheduled_time=iso, hashtags)
         ↓
4. Calls post_to_linkedin() with scheduled_time parameter
         ↓
5. Payload sets "lifecycleState": "DRAFT"
   + "scheduledPublishTime": [millisecond epoch timestamp]
         ↓
6. LinkedIn stores the post as a draft and publishes it at the scheduled time
         ↓
7. UI shows: ✅ Scheduled for 2026-03-01T09:00:00!
```

---

## 8. LinkedIn Posts API Integration

**File:** `tools/linkedin_poster.py`

### Authentication

```python
headers = {
    "Authorization": f"Bearer {self.access_token}",   # OAuth 2.0 token
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": "202601",                      # API version pin
}
```

### API Payload Structure (TEXT post)

```json
{
  "author": "urn:li:person:YOUR_USER_ID",
  "commentary": "Full post text including hashtags",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED"
}
```

### For Scheduled Posts (additional fields)

```json
{
  "lifecycleState": "DRAFT",
  "scheduledPublishTime": "1772000000000"
}
```
`scheduledPublishTime` is a **Unix timestamp in milliseconds**, converted from the ISO datetime string via `_to_ms_epoch()`.

### API Endpoint

```
POST https://api.linkedin.com/rest/posts
```

### Success Response

LinkedIn returns **HTTP 201 Created** and the `post_id` is extracted from the response header:
```
x-restli-id: urn:li:ugcPost:7123456789012345678
```

### Error Handling

If LinkedIn returns a non-201 status code, the error message is extracted from `response.json()["message"]` and surfaced in the UI as a red error banner.

### Additional Operations Available

| Method | API call | Purpose |
|---|---|---|
| `post_to_linkedin()` | `POST /rest/posts` | Publish immediately |
| `schedule_post()` | `POST /rest/posts` (DRAFT) | Schedule for future |
| `delete_post(post_id)` | `DELETE /rest/posts/{id}` | Delete a post |
| `get_post_stats(post_id)` | `GET /rest/posts/{id}` | Get post stats |

---

## 9. UI Architecture

The app has **two modes**, toggled in the Streamlit sidebar:

### Mode 1 — Simple Generation (`core/generator.py`)
A classic form-based UI. User fills in topic, tone, audience, content type, and clicks Generate. The `LinkedInGenerator` class runs a single LLM call (Simple mode) or RAG-enhanced call (Advanced mode) and returns one post.
- Rendered by: `ui/components.py`

### Mode 2 — Agentic Studio
A full multi-agent experience with real-time progress tracking for all 6 agents.
- **Input:** `ui/multi_modal_input.py` — handles text, image upload, PDF/DOCX upload, URL entry
- **Dashboard:** `ui/agent_dashboard.py` — shows animated progress cards per agent, then renders 3 variant cards with Post/Schedule/Copy/Download buttons
- **Orchestration:** `AgentOrchestrator.execute_workflow()` — runs the 6-agent pipeline
- After completion, `render_agentic_results()` displays the full `OrchestratorResult`

---

## 10. Data Models

**File:** `core/models.py`

### Key Enums

```python
class GenerationMode(Enum):
    SIMPLE   = "simple"    # Direct LLM, ~1-3 seconds
    ADVANCED = "advanced"  # RAG-enhanced, ~8-15 seconds

class ContentType(Enum):
    BUILD_IN_PUBLIC, EDUCATIONAL, HOT_TAKE,
    FOUNDER_LESSON, GITHUB_SHOWCASE, AI_INSIGHTS, LEARNING_SHARE

class Tone(Enum):
    PROFESSIONAL, CASUAL, ENTHUSIASTIC,
    THOUGHTFUL, BOLD, CONVERSATIONAL

class Audience(Enum):
    FOUNDERS, DEVELOPERS, PROFESSIONALS,
    ENTREPRENEURS, TECH_LEADERS, GENERAL
```

### Key Dataclasses

```python
@dataclass
class LLMResult:
    content:       str
    tokens_used:   int
    success:       bool
    error_message: str

@dataclass
class AgentResult:
    success:         bool
    output:          dict
    summary:         str
    context_passed:  dict    # what gets merged into shared context
    processing_time: float
    error_message:   str

@dataclass
class OrchestratorResult:
    success:                bool
    variants:               dict   # {storyteller, strategist, provocateur}
    hashtags:               str
    strategy:               dict
    research:               dict
    brand_feedback:         dict
    optimization:           dict
    overall_recommendations: list
    best_variant:           str
    total_time:             float
    agents_run:             list

@dataclass
class LinkedInPostResult:
    success:                   bool
    post_id:                   str
    post_url:                  str
    error_message:             str
    timestamp:                 str
    share_commentary_preview:  str
```

---

## 11. Configuration & Environment Variables

Create a `.env` file in the project root:

```env
# REQUIRED — LLM Provider
GROQ_API_KEY=gsk_...

# REQUIRED — LinkedIn Publishing
LINKEDIN_ACCESS_TOKEN=AQV...    # OAuth 2.0 access token
LINKEDIN_USER_ID=abc123xyz       # Your LinkedIn member ID

# OPTIONAL — LinkedIn OAuth App
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
```

### Getting LinkedIn credentials

1. Create an app at [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Add the `w_member_social` OAuth 2.0 scope
3. Complete the OAuth flow to obtain `LINKEDIN_ACCESS_TOKEN`
4. Call `https://api.linkedin.com/v2/me` to get your `LINKEDIN_USER_ID`

### Getting Groq API key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Generate an API key
3. Set `GROQ_API_KEY` in your `.env` file

---

## 12. End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INPUT (Streamlit UI)                        │
│   Text + Images + PDFs + URLs + Past Posts + Tone + Audience prefs      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       AGENT ORCHESTRATOR                                │
│                   (shared context dictionary)                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │         AGENT 1: InputProcessorAgent         │
          │  Tools: VisionAnalyzer, DocumentProcessor,   │
          │         WebScraper                           │
          │  LLM: 1 call → content synthesis             │
          │  Output: combined_content, synthesis, themes │
          └──────────────────────┬──────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │           AGENT 2: ResearchAgent             │
          │  Tools: TrendAnalyzer                        │
          │  LLM: 2 calls → market intel + gaps          │
          │  Output: hashtags, tone, trends, insights    │
          └──────────────────────┬──────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │      AGENT 3: ContentIntelligenceAgent       │
          │  LLM: 1 structured call → full strategy      │
          │  Output: strategy, 3 post angles             │
          └──────────────────────┬──────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │          AGENT 4: GenerationAgent            │
          │  LLM: 3 calls (one per variant style)        │
          │  Output: variants {storyteller,              │
          │          strategist, provocateur}            │
          └──────────────────────┬──────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │          AGENT 5: BrandVoiceAgent            │
          │  Tools: BrandAnalyzer                        │
          │  LLM: 0-3 calls (only if score < 0.7)        │
          │  Output: brand-adjusted variants             │
          └──────────────────────┬──────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────┐
          │         AGENT 6: OptimizationAgent           │
          │  Tools: EngagementPredictor, SentimentAna.   │
          │  Output: scores, best_variant, hashtags,     │
          │          recommendations                     │
          └──────────────────────┬──────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        UI: 3 VARIANT CARDS                              │
│        Storyteller ★     Strategist         Provocateur                 │
│        [Copy] [Download] [📤 Post Now] [⏰ Schedule]                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ User clicks Post Now
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   LinkedInPoster.post_to_linkedin()                     │
│    POST https://api.linkedin.com/rest/posts                             │
│    Authorization: Bearer {LINKEDIN_ACCESS_TOKEN}                        │
│    body: { author, commentary, visibility, lifecycleState }             │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP 201 Created
                                 ▼
              ┌──────────────────────────────────┐
              │  ✅ Posted! View on LinkedIn      │
              │  post_url displayed in UI         │
              └──────────────────────────────────┘
```

---

*Documentation generated from source code analysis of the LinkedIn Post Generator project.*  
*Last updated: February 2026*
