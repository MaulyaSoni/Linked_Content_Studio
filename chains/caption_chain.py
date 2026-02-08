# ============================================================================
# LINKEDIN POST GENERATOR - CAPTION CHAIN
# ============================================================================

from langchain_core.prompts import PromptTemplate
from config.settings import get_llm
from prompts.post_prompts import CAPTION_PROMPT

# Initialize LLM with moderate temperature
llm = get_llm(temperature=0.5)

# ============================================================================
# CAPTION GENERATION CHAIN (LCEL Runnable)
# ============================================================================

def create_caption_chain():
    """
    Create caption generation chain for demo/screenshot captions.
    
    Returns:
        LCEL Runnable chain for generating captions
    """
    prompt = PromptTemplate.from_template(CAPTION_PROMPT)
    return prompt | llm

# Create singleton instance
caption_generator = create_caption_chain()

def generate_caption(asset_type: str, context: str):
    """
    Generate caption for a content asset (demo/screenshot).
    
    Args:
        asset_type: Type of asset ("Video demo", "Screenshot", "Code snippet", etc.)
        context: Project context
    
    Returns:
        Generated caption (AIMessage object)
    """
    payload = {
        "asset_type": asset_type,
        "context": context,
    }
    return caption_generator.invoke(payload)
