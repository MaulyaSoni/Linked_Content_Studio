"""
GitHub-Specific LinkedIn Prompts
==============================
Specialized prompts for turning GitHub repositories into engaging LinkedIn content.
Focuses on technical storytelling and developer engagement.
"""

from typing import Dict, Any
from core.models import PostRequest, RAGContext, RepoContext


def build_github_simple_prompt(request: PostRequest) -> str:
    """
    Simple GitHub showcase prompt for repositories without deep context.
    """
    
    from core.models import get_tone_display_names, get_audience_display_names
    
    tone_name = get_tone_display_names().get(request.tone.value, request.tone.value)
    audience_name = get_audience_display_names().get(request.audience.value, request.audience.value)
    
    # Extract repo name from URL
    repo_name = request.github_url.split('/')[-1].replace('.git', '')
    repo_owner = request.github_url.split('/')[-2]
    
    prompt = f"""
You are a technical founder who builds in public and shares insights with the developer community.

Your mission: Write a compelling LinkedIn post about this GitHub repository that makes developers want to check it out.

REPOSITORY: {repo_owner}/{repo_name}
URL: {request.github_url}

TECHNICAL STORYTELLING APPROACH:
Instead of just describing what the code does, focus on:
- WHY this project matters to developers
- What PROBLEM it solves (be specific)
- What you can LEARN from the codebase
- Who should CARE about this project
- What makes it INTERESTING or unique

BUILD-IN-PUBLIC VIBES:
Write like a founder sharing a discovery, not a marketing announcement:
- "Just discovered..." or "Been exploring..." 
- Share what caught your attention
- Mention specific technical aspects that impressed you
- Connect it to broader trends or challenges
- Ask what the community thinks

TARGET AUDIENCE: {audience_name}
TONE: {tone_name} - Sound like a peer, not a salesperson

STRUCTURE FOR TECHNICAL CONTENT:
1. HOOK: What made you stop and look at this repo?
2. PROBLEM: What challenge does this solve?
3. SOLUTION: How does it solve it (briefly)?
4. IMPACT: Why should others care?
5. ENGAGEMENT: Ask for community input or experiences

AVOID:
- Generic descriptions like "This is a great project"
- Feature lists without context
- Overly promotional language 
- Technical jargon without explanation

Make it feel like a genuine recommendation from one developer to another.

FORMAT YOUR RESPONSE AS:

POST:
[Your compelling GitHub showcase post]

HASHTAGS:
[5-8 relevant tech/dev hashtags]

CAPTION:
[Brief description for video demos - only if requested]
"""
    
    return prompt.strip()


def build_github_rag_prompt(request: PostRequest, context: RAGContext) -> str:
    """
    Enhanced GitHub prompt using repository context from RAG.
    """
    
    from core.models import get_tone_display_names, get_audience_display_names
    
    tone_name = get_tone_display_names().get(request.tone.value, request.tone.value)
    audience_name = get_audience_display_names().get(request.audience.value, request.audience.value)
    
    repo_context = context.repo_context
    repo_name = repo_context.name if repo_context else "Unknown"
    
    # Build context summary
    context_summary = _build_context_summary(context)
    
    prompt = f"""
You are a technical expert who turns complex repositories into engaging LinkedIn stories.

Transform this GitHub repository analysis into a compelling post for {audience_name.lower()}.

REPOSITORY ANALYSIS:
{context_summary}

FULL CONTEXT:
{context.content}

STORYTELLING STRATEGY:
Don't just summarize the README. Instead, extract the most interesting insights:

1. IDENTIFY THE "WHY" - What problem does this solve that developers face?
2. HIGHLIGHT THE "HOW" - What makes the technical approach interesting?
3. EXTRACT THE "LESSON" - What can others learn from this codebase?
4. FIND THE "HOOK" - What would make developers want to explore this?

BUILD-IN-PUBLIC APPROACH:
- Share it like a discovery you want others to know about
- Mention specific technical details that caught your eye
- Connect it to broader development trends or challenges
- Position it as "here's something worth your time" not "here's an ad"

TECHNICAL DEPTH FOR {audience_name}:
{"Focus on implementation details, architecture decisions, and code quality" if "developers" in audience_name.lower() else "Keep technical details accessible but focus on business impact and innovation"}

TARGET TONE: {tone_name}

ENGAGEMENT STRATEGY:
End with a question that:
- Asks about similar projects or experiences
- Seeks opinions on the technical approach  
- Invites discussion about the problem domain
- Asks what features they'd add or change

FORMAT YOUR RESPONSE AS:

POST:
[Your engaging LinkedIn post about the repository]

HASHTAGS:
[6-8 relevant hashtags mixing tech topics and broader themes]

CAPTION:  
[Video walkthrough description - only if requested]
"""
    
    return prompt.strip()


def build_project_launch_prompt(request: PostRequest, context: RAGContext = None) -> str:
    """
    Prompt for announcing your own GitHub project launch.
    """
    
    context_info = ""
    if context and context.repo_context:
        context_info = f"""
PROJECT DETAILS:
- Repository: {context.repo_context.name}
- Tech Stack: {', '.join(context.repo_context.dependencies[:5]) if context.repo_context.dependencies else 'Various technologies'}
- Description: {context.repo_context.description}
"""
    
    prompt = f"""
You are a founder launching your project and building in public on LinkedIn.

Write a project launch announcement that feels authentic and gets developers excited.

{context_info}

PROJECT LAUNCH STORYTELLING:
This should NOT sound like a press release. Instead:

1. START WITH THE PROBLEM: What frustrated you enough to build this?
2. SHARE THE JOURNEY: Briefly mention why you built it (learning, solving own problem, etc.)
3. HIGHLIGHT WHAT'S COOL: What are you proud of technically?
4. BE HONEST: What was challenging? What did you learn?
5. INVITE EXPLORATION: Ask for feedback, contributions, or just thoughts

AUTHENTIC FOUNDER VOICE:
- Use "I built" or "We created" not "Introducing our new product"
- Mention what you learned during development
- Share what you're excited about technically  
- Be humble but confident about what you've created
- Ask for genuine feedback, not just promotion

STRUCTURE:
1. Problem/motivation hook
2. Brief journey or challenge  
3. What you built and why it matters
4. Technical highlights (1-2 key features)
5. Call for feedback/engagement

Make it feel like sharing with friends, not announcing to customers.

FORMAT YOUR RESPONSE AS:

POST:
[Your authentic project launch post]

HASHTAGS:
[Mix of technical and entrepreneurship hashtags]

CAPTION:
[Demo video description - only if requested]
"""
    
    return prompt.strip()


def build_technical_deep_dive_prompt(request: PostRequest, context: RAGContext) -> str:
    """
    Prompt for technical deep-dive posts about specific implementations.
    """
    
    prompt = f"""
You are a senior developer sharing technical insights with the engineering community.

Turn this repository analysis into a technical deep-dive post that teaches something valuable.

REPOSITORY CONTEXT:
{context.content}

TECHNICAL EDUCATION FOCUS:
Extract the most educational aspects:
- Interesting architectural decisions
- Creative problem-solving approaches  
- Performance optimizations
- Security considerations
- Scalability patterns
- Developer experience improvements

EDUCATIONAL POST STRUCTURE:
1. TECHNICAL HOOK: Start with the most interesting technical insight
2. PROBLEM CONTEXT: Why was this technical decision needed?
3. SOLUTION BREAKDOWN: How does it work? (be specific but accessible)
4. LESSONS: What can others apply to their own projects?
5. DISCUSSION: Ask about alternative approaches or experiences

TECHNICAL WRITING STYLE:
- Use specific examples and code concepts
- Explain the "why" behind technical choices
- Include performance impacts or trade-offs
- Make it educational, not just descriptive
- Balance depth with accessibility

TARGET: Senior developers and architects who want to learn from real implementations.

FORMAT YOUR RESPONSE AS:

POST:
[Your technical deep-dive post]

HASHTAGS:
[Technical hashtags focusing on architecture, performance, and specific technologies]

CAPTION:
[Technical walkthrough description - only if requested]
"""
    
    return prompt.strip()


def _build_context_summary(context: RAGContext) -> str:
    """Build a concise summary of repository context for prompting."""
    
    if not context.repo_context:
        return "Repository information extracted from available sources."
    
    repo = context.repo_context
    
    summary_parts = []
    
    # Basic info
    summary_parts.append(f"Repository: {repo.name}")
    if repo.description:
        summary_parts.append(f"Purpose: {repo.description}")
    
    # Technical details  
    if repo.language:
        summary_parts.append(f"Primary Language: {repo.language}")
    if repo.dependencies:
        tech_stack = ", ".join(repo.dependencies[:5])
        summary_parts.append(f"Tech Stack: {tech_stack}")
    
    # Project health
    if repo.stars > 0:
        summary_parts.append(f"Stars: {repo.stars}")
    if repo.topics:
        topics = ", ".join(repo.topics[:3])
        summary_parts.append(f"Topics: {topics}")
    
    # Context quality
    sources = ", ".join(context.sources_used)
    summary_parts.append(f"Data Sources: {sources}")
    
    return "\n".join(f"- {part}" for part in summary_parts)


def route_github_prompt(request: PostRequest, context: RAGContext = None) -> str:
    """
    Route GitHub requests to appropriate prompt based on content type.
    """
    
    content_type = request.content_type.value
    
    if content_type == "build_in_public":
        return build_project_launch_prompt(request, context)
    elif content_type == "educational":
        return build_technical_deep_dive_prompt(request, context) if context else build_github_simple_prompt(request)
    else:
        # Default to showcase prompt
        return build_github_rag_prompt(request, context) if context else build_github_simple_prompt(request)


# Content quality validators for GitHub posts
def validate_github_post(post_content: str, repo_context: RepoContext = None) -> Dict[str, bool]:
    """Validate GitHub post follows technical storytelling best practices."""
    
    validation = {
        "mentions_problem": any(
            keyword in post_content.lower() 
            for keyword in ["problem", "challenge", "issue", "solves", "addresses"]
        ),
        "includes_technical_detail": any(
            keyword in post_content.lower()
            for keyword in ["built", "implemented", "uses", "architecture", "performance"]
        ),
        "has_call_to_action": post_content.strip().endswith('?'),
        "appropriate_length": 150 <= len(post_content) <= 2500,
        "not_too_promotional": post_content.lower().count('check out') <= 1
    }
    
    if repo_context:
        validation["mentions_repo_name"] = repo_context.name.lower() in post_content.lower()
    
    return validation


if __name__ == "__main__":
    # Test GitHub prompt building
    from core.models import PostRequest, ContentType, Tone, Audience
    
    test_request = PostRequest(
        content_type=ContentType.GITHUB_SHOWCASE,
        github_url="https://github.com/microsoft/vscode",
        tone=Tone.ENTHUSIASTIC,
        audience=Audience.DEVELOPERS
    )
    
    prompt = build_github_simple_prompt(test_request)
    print("GitHub prompt length:", len(prompt))
    print("Preview:", prompt[:300] + "...")