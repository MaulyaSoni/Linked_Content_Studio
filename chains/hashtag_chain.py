# ============================================================================
# LINKEDIN POST GENERATOR - HASHTAG CHAIN
# ============================================================================

from langchain_core.prompts import PromptTemplate
from config.settings import get_llm_deterministic
from prompts.post_prompts import HASHTAG_PROMPT

# Initialize LLM with low temperature for consistent output
llm = get_llm_deterministic()

# ============================================================================
# HASHTAG GENERATION CHAIN (LCEL Runnable)
# ============================================================================

def create_hashtag_chain():
    """
    Create hashtag generation chain.
    
    Returns:
        LCEL Runnable chain for generating hashtags
    """
    prompt = PromptTemplate.from_template(HASHTAG_PROMPT)
    return prompt | llm

# Create singleton instance
hashtag_generator = create_hashtag_chain()

def generate_hashtags(content: str, context: str):
    """
    Generate hashtags for LinkedIn post.
    
    Args:
        content: Post content text
        context: Project context
    
    Returns:
        Generated hashtags (AIMessage object)
    """
    payload = {
        "content": content,
        "context": context,
    }
    return hashtag_generator.invoke(payload)
