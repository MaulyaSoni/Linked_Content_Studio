from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from app.services.user_profiling_service import StyleProfile
from app.services.llm_service import LLMService
from app.services.fact_checking_service import FactCheckingService
import json


class PostGenerationState(TypedDict):
    """State for post generation workflow."""
    
    # Inputs
    user_id: str
    topic: str
    tone: str
    audience: str
    context: Optional[str]
    
    # Intermediate steps
    user_profile: Optional[dict]
    user_style: Optional[dict]
    research_findings: Optional[dict]
    strategy: Optional[dict]
    
    # Outputs
    variants: List[str]
    selected_variant: Optional[str]
    hashtags: Optional[List[str]]
    fact_check_result: Optional[dict]
    quality_score: Optional[float]
    final_post: Optional[str]
    
    # Metadata
    agent_feedback: List[str]
    errors: List[str]


class PostGenerationWorkflow:
    """LangGraph-based post generation workflow."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.fact_checker = FactCheckingService()
        self.graph = StateGraph(PostGenerationState)
        self._build_graph()
    
    def _build_graph(self):
        """Build the workflow graph."""
        
        # Add nodes (each is an async function)
        self.graph.add_node("load_user_profile", self._load_user_profile)
        self.graph.add_node("load_user_style", self._load_user_style)
        self.graph.add_node("research", self._research_agent)
        self.graph.add_node("develop_strategy", self._strategy_agent)
        self.graph.add_node("generate_variants", self._generate_variants)
        self.graph.add_node("fact_check", self._fact_check)
        self.graph.add_node("quality_score", self._quality_score)
        
        # Set entry point
        self.graph.set_entry_point("load_user_profile")
        
        # Add edges (order of execution)
        self.graph.add_edge("load_user_profile", "load_user_style")
        self.graph.add_edge("load_user_style", "research")
        self.graph.add_edge("research", "develop_strategy")
        self.graph.add_edge("develop_strategy", "generate_variants")
        self.graph.add_edge("generate_variants", "fact_check")
        self.graph.add_edge("fact_check", "quality_score")
        
        # Conditional edge: if score low, regenerate; else continue
        self.graph.add_conditional_edges(
            "quality_score",
            self._should_regenerate,
            {
                "regenerate": "generate_variants",
                "proceed": END,
            }
        )
        
        # Compile
        self.compiled = self.graph.compile()
    
    async def execute(self, state: PostGenerationState) -> PostGenerationState:
        """Execute the workflow."""
        
        result = await self.compiled.ainvoke(state)
        return result
    
    # Node functions
    async def _load_user_profile(self, state: PostGenerationState) -> dict:
        """Load user profile and preferences."""
        # In production, load from database
        return {
            **state,
            "user_profile": {"user_id": state["user_id"]},
        }
    
    async def _load_user_style(self, state: PostGenerationState) -> dict:
        """Load user's writing style profile."""
        # In production, load from database or vector DB
        # For now, use default style
        style = StyleProfile.default(state["user_id"])
        return {
            **state,
            "user_style": style.dict(),
        }
    
    async def _research_agent(self, state: PostGenerationState) -> dict:
        """Research topic and find relevant information."""
        
        prompt = f"""
        Research the topic: {state['topic']}
        
        Provide:
        1. Key talking points (3-5)
        2. Recent trends or statistics
        3. Common perspectives or debates
        
        Target audience: {state.get('audience', 'general professionals')}
        
        Format as JSON with keys: talking_points, trends, perspectives
        """
        
        response = await self.llm_service.generate(prompt)
        
        try:
            research = json.loads(response.content)
        except:
            research = {"talking_points": [], "trends": [], "perspectives": []}
        
        return {
            **state,
            "research_findings": research,
        }
    
    async def _strategy_agent(self, state: PostGenerationState) -> dict:
        """Develop content strategy."""
        
        research = state.get("research_findings", {})
        
        strategy = {
            "angle": "educational",
            "hook_style": "question",
            "structure": "problem-solution",
            "key_message": research.get("talking_points", [""])[0] if research.get("talking_points") else state["topic"],
        }
        
        return {
            **state,
            "strategy": strategy,
        }
    
    async def _generate_variants(self, state: PostGenerationState) -> dict:
        """Generate 3 post variants."""
        
        from app.services.user_profiling_service import StyleProfile
        
        user_style = StyleProfile(**state["user_style"]) if state.get("user_style") else StyleProfile.default(state["user_id"])
        
        variants = []
        angles = ["storyteller", "strategist", "provocateur"]
        
        for angle in angles:
            prompt = self._create_generation_prompt(
                topic=state["topic"],
                strategy=state.get("strategy", {}),
                style=user_style,
                angle=angle,
                tone=state["tone"],
                research=state.get("research_findings", {})
            )
            
            variant = await self.llm_service.generate(prompt)
            variants.append(variant.content)
        
        return {
            **state,
            "variants": variants,
        }
    
    async def _fact_check(self, state: PostGenerationState) -> dict:
        """Fact-check the best variant."""
        
        best_variant = state["variants"][0] if state["variants"] else ""
        
        if best_variant:
            check_result = await self.fact_checker.fact_check_post(
                best_variant,
                context={"user_id": state["user_id"]}
            )
            
            return {
                **state,
                "fact_check_result": check_result.to_dict(),
            }
        
        return state
    
    async def _quality_score(self, state: PostGenerationState) -> dict:
        """Score post quality."""
        
        post = state["variants"][0] if state["variants"] else ""
        fact_check = state.get("fact_check_result", {})
        
        if not post:
            return {**state, "quality_score": 0}
        
        # Calculate quality based on multiple factors
        fact_score = fact_check.get("confidence_score", 50)
        length_score = min(100, len(post.split()) / 2)  # Ideal: 200 words
        structure_score = 80 if post.count("\n\n") >= 3 else 60
        
        quality = (fact_score * 0.4) + (length_score * 0.3) + (structure_score * 0.3)
        
        return {
            **state,
            "quality_score": round(quality, 2),
            "final_post": post,
        }
    
    async def _should_regenerate(self, state: PostGenerationState) -> str:
        """Decide whether to regenerate based on quality score."""
        
        if state.get("quality_score", 0) < 60:
            return "regenerate"
        else:
            return "proceed"
    
    def _create_generation_prompt(
        self,
        topic: str,
        strategy: dict,
        style,
        angle: str,
        tone: str,
        research: dict
    ) -> str:
        """Create a generation prompt with style injection."""
        
        angle_prompts = {
            "storyteller": "Start with a compelling story or personal experience",
            "strategist": "Lead with data, insights, and strategic thinking",
            "provocateur": "Challenge conventional wisdom with a contrarian view",
        }
        
        talking_points = research.get("talking_points", [])
        
        prompt = f"""
        {angle_prompts.get(angle, '')}
        
        Write a LinkedIn post about: {topic}
        
        Style Guidelines:
        - Tone: {tone}
        - Vocabulary: {style.vocabulary}
        - Personality: {style.personality}
        - Use emojis: {'Yes' if style.emoji_usage else 'No'}
        - CTA style: {style.cta_preference}
        - Average sentence length: {style.structure.get('avg_length', 15)} words
        
        Key points to include:
        {chr(10).join(f"- {point}" for point in talking_points[:3])}
        
        Requirements:
        1. Strong hook in first line
        2. 150-300 words
        3. Clear structure with line breaks
        4. End with {style.cta_preference}
        5. Add 3-5 relevant hashtags
        
        Post:
        """
        
        return prompt.strip()
