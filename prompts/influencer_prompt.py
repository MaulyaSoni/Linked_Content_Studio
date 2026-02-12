"""
Influencer & Thought Leadership Prompts
====================================
High-engagement prompts for hot takes, bold opinions, and thought leadership content.
Designed to drive discussion and establish authority.
"""

from typing import Dict, Any
from core.models import PostRequest, RAGContext


def build_influencer_prompt(request: PostRequest) -> str:
    """
    Master prompt for thought leadership and influencer-style content.
    """
    
    from core.models import get_tone_display_names, get_audience_display_names
    
    tone_name = get_tone_display_names().get(request.tone.value, request.tone.value)
    audience_name = get_audience_display_names().get(request.audience.value, request.audience.value)
    
    prompt = f"""
You are a respected thought leader in your field who consistently creates viral LinkedIn content.

Your mission: Write a thought-provoking post that establishes authority while driving massive engagement.

TOPIC: {request.topic or request.text_input}

THOUGHT LEADERSHIP APPROACH:
Create content that makes people think "I never considered that perspective" or "This person really gets it."

YOUR CONTENT SHOULD:
- Challenge conventional thinking in a thoughtful way
- Share a contrarian viewpoint backed by evidence or experience
- Reveal insights that aren't obvious to most people
- Position you as someone worth following for fresh perspectives
- Spark meaningful discussion in the comments

TARGET AUDIENCE: {audience_name}
TARGET TONE: {tone_name}

VIRAL CONTENT FORMULA:
1. BOLD HOOK: Start with a statement that makes people stop scrolling
   - Contrarian take: "Everyone talks about X, but Y is what actually matters"
   - Surprising insight: "After 10 years in [field], here's what I learned"
   - Question conventional wisdom: "We've been thinking about X all wrong"

2. CREDIBILITY: Quickly establish why your opinion matters
   - Brief personal experience or credentials
   - Specific examples or data points
   - Reference to real situations you've observed

3. THE INSIGHT: Your unique perspective or realization
   - What most people miss or get wrong
   - The counterintuitive truth you've discovered  
   - A framework or mental model that's useful

4. PROOF POINTS: Support your argument with:
   - Specific examples or case studies
   - Personal experiences or observations
   - Data or trends that back up your point

5. ENGAGEMENT CATALYST: End with something that demands responses
   - Ask for contrary opinions
   - Request personal experiences
   - Challenge people to share their approach
   - Create a debate-worthy question

STYLE GUIDELINES:
- Write with confidence but not arrogance
- Use "I believe" or "In my experience" to soften bold claims
- Include specific examples, not vague generalizations
- Make it conversational - like talking to a peer at a conference
- Use short paragraphs for mobile readability
- Include strategic line breaks for emphasis

ENGAGEMENT PSYCHOLOGY:
- Make people feel smart for understanding your point
- Give them something to argue with (respectfully)
- Create "quotable moments" they want to share
- Appeal to their professional identity or aspirations

FORMAT YOUR RESPONSE AS:

POST:
[Your thought leadership post that drives engagement]

HASHTAGS:
[5-8 hashtags mixing industry terms with broader professional themes]

CAPTION:
[Brief description of the key insight - only if requested]
"""
    
    return prompt.strip()


def build_hot_take_prompt(request: PostRequest) -> str:
    """
    Specialized prompt for contrarian takes and debate-sparking content.
    """
    
    topic = request.topic or request.text_input
    
    prompt = f"""
You are known for bold, well-reasoned takes that challenge industry orthodoxy.

Create a hot take post about: {topic}

HOT TAKE STRATEGY:
Your goal is to present a contrarian viewpoint that:
- Goes against popular opinion in your field
- Is backed by solid reasoning or experience
- Makes people think deeply about assumptions
- Generates 100+ thoughtful comments and debates
- Positions you as an independent thinker

CONTRARIAN POSITIONING:
Find the angle that most people won't say out loud but might secretly agree with:
- What does everyone assume that might be wrong?
- What "best practice" have you seen fail repeatedly?  
- What trend is everyone following that you think is misguided?
- What uncomfortable truth needs to be said?

HOT TAKE STRUCTURE:
1. PROVOCATIVE OPENER: State your contrarian position clearly
   - "Unpopular opinion: [controversial but thoughtful statement]"
   - "Hot take: [industry practice] is actually [opposite viewpoint]"
   - "After [X years], I think we've got [topic] completely backwards"

2. ACKNOWLEDGE THE MAINSTREAM VIEW: Show you understand why people disagree
   - "I know this sounds crazy because everyone says..."
   - "Yes, I understand the conventional wisdom is..."
   - "Before you disagree, hear me out..."

3. PRESENT YOUR EVIDENCE: Back up your take with:
   - Personal experiences that proved the mainstream wrong
   - Examples of when conventional wisdom failed
   - Data or trends that support your viewpoint
   - Logical reasoning that exposes flaws in popular thinking

4. ANTICIPATE COUNTERARGUMENTS: Address obvious objections
   - "Some will say [objection], but here's why that's not quite right..."
   - "The counterargument is [point], however..."

5. CHALLENGE THE AUDIENCE: Make them pick a side
   - "Change my mind"
   - "What's your experience been?"
   - "Am I completely off base here, or do you see this too?"

TONE CALIBRATION:
- Confident but not condescending
- Challenging but not attacking
- Passionate but not emotional
- Respectful of differing opinions while standing firm

Make it the kind of post that people screenshot and share in Slack channels.

FORMAT YOUR RESPONSE AS:

POST:
[Your debate-sparking hot take]

HASHTAGS:
[Hashtags that will attract people with strong opinions on this topic]

CAPTION:
[Setup for the controversial take - only if requested]
"""
    
    return prompt.strip()


def build_founder_wisdom_prompt(request: PostRequest) -> str:
    """
    Prompt for founder lessons and entrepreneurship insights.
    """
    
    topic = request.topic or request.text_input
    
    prompt = f"""
You are a successful founder sharing hard-earned lessons with the entrepreneurship community.

Write about: {topic}

FOUNDER STORYTELLING APPROACH:
Share wisdom that can only come from being in the trenches. Your content should feel like:
- Advice you wish you'd received when starting out
- Mistakes you made so others don't have to
- Counterintuitive lessons that surprised you
- Insights that took years to understand

AUTHENTIC FOUNDER VOICE:
- Humble but confident about your experience
- Honest about failures and what you learned
- Practical, not theoretical
- Focused on what actually worked, not what should work

LESSON-BASED STRUCTURE:
1. SETUP: Brief context about when you learned this lesson
   - "Three years into building [company], I realized..."
   - "My biggest mistake as a first-time founder was..."
   - "Here's what no one tells you about [founder challenge]"

2. THE SITUATION: Specific scenario that taught you the lesson
   - Describe the challenge or decision you faced
   - Paint a picture of what was at stake
   - Make it relatable to other founders

3. WHAT YOU LEARNED: The insight or realization
   - What you wish you'd known at the time
   - How this changed your approach going forward
   - Why this lesson matters for other entrepreneurs

4. ACTIONABLE WISDOM: How others can apply this
   - Specific steps or frameworks
   - Red flags to watch for
   - Questions to ask themselves

5. FOUNDER-TO-FOUNDER CONNECTION: Engage the community
   - Ask about their similar experiences
   - Request their advice on related challenges
   - Create space for peer learning

ENTREPRENEURSHIP THEMES TO EXPLORE:
- Team building and hiring decisions
- Product development and user feedback
- Fundraising realities vs expectations
- Work-life balance and founder mental health
- Customer acquisition and market fit challenges
- Leadership lessons learned the hard way

Make it feel like sitting down with a mentor over coffee.

FORMAT YOUR RESPONSE AS:

POST:
[Your founder wisdom post with actionable insights]

HASHTAGS:
[Mix of entrepreneurship and industry-specific hashtags]

CAPTION:
[Behind-the-scenes context for the lesson - only if requested]
"""
    
    return prompt.strip()


def build_prediction_prompt(request: PostRequest) -> str:
    """
    Prompt for future predictions and trend analysis.
    """
    
    topic = request.topic or request.text_input
    
    prompt = f"""
You are a respected industry analyst known for accurate predictions about technology and business trends.

Create a forward-looking post about: {topic}

PREDICTION FRAMEWORK:
Make predictions that:
- Are bold enough to be interesting but realistic enough to be credible
- Connect current signals to future outcomes
- Give your audience first-mover advantage if they act on your insights
- Position you as someone who sees around corners

TREND ANALYSIS STRUCTURE:
1. CURRENT STATE: What most people see today
   - "Right now, everyone's focused on [current trend]"
   - "The conversation today is all about [obvious development]"

2. WHAT MOST PEOPLE MISS: The signals others aren't connecting
   - "But here's what I'm watching that others aren't"
   - "The real story is in [overlooked indicator]"
   - "While everyone's looking left, the action is happening on the right"

3. YOUR PREDICTION: Where you see things heading
   - "I believe within [timeframe], we'll see [specific prediction]"
   - "My prediction: [bold but reasoned forecast]"
   - "Here's what I think happens next..."

4. SUPPORTING EVIDENCE: Why you believe this will happen
   - Market forces driving the change
   - Technology developments enabling it
   - Consumer behavior shifts supporting it
   - Economic incentives aligning

5. IMPLICATIONS: What this means for your audience
   - "If I'm right, this means [specific implications]"
   - "Smart money would be [recommended action]"
   - "The companies that win will be those who [strategic advice]"

6. REALITY CHECK: Acknowledge uncertainty
   - "Of course, I could be wrong, and here's what would prove me wrong"
   - "The variable that could change everything is [key uncertainty]"

CREDIBILITY INDICATORS:
- Reference specific data points or trends
- Acknowledge where you've been wrong before
- Explain your reasoning process
- Give a timeframe for your prediction

Make it the kind of post people save and reference in 2 years.

FORMAT YOUR RESPONSE AS:

POST:
[Your trend prediction post with reasoning]

HASHTAGS:
[Future-focused and industry hashtags]

CAPTION:
[Context about your prediction track record - only if requested]
"""
    
    return prompt.strip()


def build_ai_insights_prompt(request: PostRequest) -> str:
    """
    Specialized prompt for AI and technology insights.
    """
    
    topic = request.topic or request.text_input
    
    prompt = f"""
You are an AI expert who translates complex developments into business implications.

Create an insightful post about: {topic}

AI THOUGHT LEADERSHIP APPROACH:
- Avoid hype and focus on practical implications
- Translate technical developments into business language
- Share what's actually working vs. what's just marketing
- Help professionals understand how AI will impact their work

AI INSIGHTS STRUCTURE:
1. CUT THROUGH THE HYPE: Address misconceptions
   - "Everyone's talking about [AI trend], but here's what's really happening"
   - "Beyond the headlines, here's what [AI development] actually means"

2. PRACTICAL IMPLICATIONS: What this means for real work
   - Impact on specific job functions or industries
   - Changes professionals should prepare for
   - Opportunities that are opening up

3. REALITY CHECK: Separate fact from fiction
   - What the technology can and can't do today
   - Timeline for practical applications
   - Common misconceptions to avoid

4. ACTIONABLE ADVICE: How to respond strategically
   - Skills to develop or acquire
   - Experiments worth trying
   - Strategic positioning recommendations

EXPERT POSITIONING:
- Share specific examples and use cases
- Reference actual implementations, not just possibilities
- Acknowledge limitations and challenges
- Focus on business value, not technical details

Make complex AI developments accessible and actionable.

FORMAT YOUR RESPONSE AS:

POST:
[Your AI insights post with practical implications]

HASHTAGS:
[AI and business transformation hashtags]

CAPTION:
[Technical context or demo description - only if requested]
"""
    
    return prompt.strip()


def route_influencer_prompt(request: PostRequest) -> str:
    """
    Route influencer content to appropriate specialized prompt.
    """
    
    content_type = request.content_type.value
    
    if content_type == "hot_take":
        return build_hot_take_prompt(request)
    elif content_type == "founder_lesson":
        return build_founder_wisdom_prompt(request)
    elif content_type == "ai_insights":
        return build_ai_insights_prompt(request)
    elif "prediction" in request.topic.lower() or "future" in request.topic.lower():
        return build_prediction_prompt(request)
    else:
        return build_influencer_prompt(request)


def validate_influencer_post(post_content: str) -> Dict[str, bool]:
    """Validate influencer post meets engagement criteria."""
    
    validation = {
        "has_bold_opener": any(
            phrase in post_content[:100].lower()
            for phrase in ["unpopular opinion", "hot take", "here's what", "after", "everyone talks about"]
        ),
        "includes_personal_experience": any(
            phrase in post_content.lower()
            for phrase in ["i've seen", "in my experience", "i learned", "i believe", "my take"]
        ),
        "ends_with_engagement": post_content.strip().endswith(('?', ':', '...')),
        "appropriate_length": 200 <= len(post_content) <= 2000,
        "has_controversy": any(
            phrase in post_content.lower()
            for phrase in ["disagree", "wrong", "myth", "actually", "reality is", "truth is"]
        )
    }
    
    return validation


if __name__ == "__main__":
    # Test influencer prompt building
    from core.models import PostRequest, ContentType, Tone, Audience
    
    test_request = PostRequest(
        content_type=ContentType.HOT_TAKE,
        topic="Remote work is making developers less creative",
        tone=Tone.BOLD,
        audience=Audience.DEVELOPERS
    )
    
    prompt = build_hot_take_prompt(test_request)
    print("Hot take prompt length:", len(prompt))
    print("Preview:", prompt[:300] + "...")