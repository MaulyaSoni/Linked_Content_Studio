# ============================================================================
# LINKEDIN POST GENERATOR - QUALITY & SPECIFICITY CHAINS
# Improvements: #1 (Specificity Enforcer), #5 (Quality Scorer)
# ============================================================================

from langchain_core.prompts import PromptTemplate
from config.settings import get_llm_deterministic
from prompts.post_prompts import SPECIFICITY_CHECK_PROMPT, QUALITY_SCORE_PROMPT

# Initialize LLM with deterministic settings for quality checks
llm = get_llm_deterministic()

# ============================================================================
# SPECIFICITY ENFORCER CHAIN - IMPROVEMENT #1
# ============================================================================

def create_specificity_chain():
    """
    Second-pass chain that improves post specificity.
    
    Checks for:
    - Real problems mentioned (not abstract)
    - One concrete technical decision
    - Metrics grounded in context
    - Prevents hallucination
    
    Returns:
        LCEL Runnable chain
    """
    prompt = PromptTemplate.from_template(SPECIFICITY_CHECK_PROMPT)
    return prompt | llm

# Create singleton instance
specificity_enforcer = create_specificity_chain()

def enforce_specificity(post: str, context: str):
    """
    Run specificity check on generated post.
    
    Args:
        post: Generated LinkedIn post
        context: Retrieved project context
    
    Returns:
        Improved post (AIMessage object)
    """
    payload = {
        "post": post,
        "context": context,
    }
    return specificity_enforcer.invoke(payload)

# ============================================================================
# QUALITY SCORE CHAIN - IMPROVEMENT #5
# ============================================================================

def create_quality_score_chain():
    """
    Evaluates post quality on three dimensions.
    
    Dimensions:
    - Clarity (message, no jargon)
    - Technical Credibility (sounds authoritative, grounded)
    - Engagement Potential (scroll-stopping, tension)
    
    Returns:
        LCEL Runnable chain
    """
    prompt = PromptTemplate.from_template(QUALITY_SCORE_PROMPT)
    return prompt | llm

# Create singleton instance
quality_scorer = create_quality_score_chain()

def score_post_quality(post: str, context: str):
    """
    Score a LinkedIn post on multiple dimensions.
    
    Args:
        post: Generated LinkedIn post
        context: Retrieved project context
    
    Returns:
        Quality score evaluation (AIMessage object)
    """
    payload = {
        "post": post,
        "context": context,
    }
    return quality_scorer.invoke(payload)

# ============================================================================
# OPTIONAL: Parse quality score for UI display
# ============================================================================

def parse_quality_score(score_text: str):
    """
    Parse quality score output for cleaner display.
    
    Args:
        score_text: Raw score output from LLM
    
    Returns:
        Dict with parsed scores
    """
    try:
        lines = score_text.split('\n')
        result = {}
        for line in lines:
            if '**' in line and ':' in line:
                # Extract metric and score
                key = line.split('**')[1] if '**' in line else ""
                if '/' in line:
                    value = line.split('/')[-2].split()[-1]
                    result[key] = value
        return result
    except:
        return {"raw": score_text}
