# ============================================================================
# LINKEDIN POST GENERATOR - STYLE CHAINS (LCEL RUNNABLES)
# ============================================================================

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from config.settings import get_llm
from prompts import post_prompts

# Initialize LLM
llm = get_llm(temperature=0.6)
llm_creative = get_llm(temperature=0.7)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def prepare_input(x):
    """Prepare input dictionary for prompt."""
    return {
        "context": x.get("context", ""),
        "tone": x.get("tone", ""),
    }

# ============================================================================
# STYLE CHAINS (Each as a Runnable)
# ============================================================================

def create_style_chain(template: str, creative: bool = False):
    """
    Create a style chain using LCEL Runnable pattern.
    
    Args:
        template: Prompt template string with {context} and {tone} placeholders
        creative: Use higher temperature for more creative output
    
    Returns:
        LCEL Runnable chain
    """
    prompt = PromptTemplate.from_template(template)
    model = llm_creative if creative else llm
    
    return (
        RunnablePassthrough()
        | RunnableLambda(prepare_input)
        | prompt
        | model
    )

# Create style-specific chains
growth_post_chain = create_style_chain(post_prompts.GROWTH_POST, creative=False)
learning_post_chain = create_style_chain(post_prompts.LEARNING_POST, creative=True)
build_in_public_chain = create_style_chain(post_prompts.BUILD_IN_PUBLIC_POST, creative=True)
recruiter_post_chain = create_style_chain(post_prompts.RECRUITER_POST, creative=False)

# ============================================================================
# MASTER STYLE SELECTOR (Runnable)
# ============================================================================

def get_style_chain(style: str):
    """
    Get the appropriate style chain based on style name.
    
    Args:
        style: Style name ("Growth", "Learning", "Build in Public", "Recruiter")
    
    Returns:
        LCEL Runnable chain for selected style
    """
    chains = {
        "Growth": growth_post_chain,
        "Learning": learning_post_chain,
        "Build in Public": build_in_public_chain,
        "Recruiter": recruiter_post_chain,
    }
    
    return chains.get(style, growth_post_chain)  # Default to Growth

# ============================================================================
# POST GENERATION CHAIN (Full Pipeline)
# ============================================================================

class PostGenerationChain:
    """Main chain for generating LinkedIn posts."""
    
    def __init__(self):
        self.style_chains = {
            "Growth": growth_post_chain,
            "Learning": learning_post_chain,
            "Build in Public": build_in_public_chain,
            "Recruiter": recruiter_post_chain,
        }
    
    def run(self, context: str, style: str, tone: str):
        """
        Generate a LinkedIn post.
        
        Args:
            context: Project context/README content
            style: Post style ("Growth", "Learning", "Build in Public", "Recruiter")
            tone: Tone description from tone_mapper
        
        Returns:
            Generated post (AIMessage object)
        """
        payload = {
            "context": context,
            "tone": tone,
        }
        
        chain = self.style_chains.get(style, self.style_chains["Growth"])
        result = chain.invoke(payload)
        return result

# Create singleton instance
post_generator = PostGenerationChain()

# ============================================================================
# HOOK GENERATOR CHAIN - IMPROVEMENT #4
# ============================================================================

def create_hook_generator():
    """
    Generate multiple hook options for user selection.
    
    Instead of one hook, generates 3 different framing options:
    - Curiosity-driven
    - Assumption-challenging
    - Outcome-driven
    
    Returns:
        LCEL Runnable chain
    """
    prompt = PromptTemplate.from_template(post_prompts.MULTIPLE_HOOKS_PROMPT)
    return prompt | llm_creative

# Create singleton instance
hook_generator = create_hook_generator()

def generate_multiple_hooks(context: str):
    """
    Generate 3 different hook options.
    
    Args:
        context: Retrieved project context
    
    Returns:
        Text with 3 hook options (AIMessage object)
    """
    payload = {"context": context}
    return hook_generator.invoke(payload)
