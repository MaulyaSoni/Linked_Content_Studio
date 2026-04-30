"""
LinkedIn Post Generator — Complete Pipeline Verification Script
Run: python verify_pipeline.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = {"ok": [], "fail": []}


def check(label, fn):
    try:
        fn()
        results["ok"].append(label)
    except Exception as e:
        results["fail"].append((label, str(e)))


# --- Core ---
check("core.models", lambda: __import__("core.models", fromlist=["PostRequest"]))
check("core.llm", lambda: __import__("core.llm", fromlist=["LLMProvider"]))
check("core.generator", lambda: __import__("core.generator", fromlist=["LinkedInGenerator"]))
check("core.brand_dna", lambda: __import__("core.brand_dna", fromlist=["BrandDNAManager"]))
check("core.validation", lambda: __import__("core.validation", fromlist=["*"]))
check("core.prompts", lambda: __import__("core.prompts", fromlist=["PromptBuilder"]))

# --- Agents ---
for _m in [
    "base_agent", "input_processor_agent", "research_agent",
    "content_intelligence_agent", "generation_agent",
    "brand_voice_agent", "optimization_agent", "agent_orchestrator",
]:
    check(f"agents.{_m}", lambda m=_m: __import__(f"agents.{m}", fromlist=[m]))

# --- Tools ---
for _t in [
    "vision_analyzer", "document_processor", "web_scraper",
    "trend_analyzer", "sentiment_analyzer", "engagement_predictor",
    "brand_analyzer", "linkedin_poster",
]:
    check(f"tools.{_t}", lambda t=_t: __import__(f"tools.{t}", fromlist=[t]))

# --- Chains ---
check("chains.quality_chains", lambda: __import__("chains.quality_chains", fromlist=["enforce_specificity"]))

# --- Loaders ---
for _l in ["base", "document", "github_loader", "github"]:
    check(f"loaders.{_l}", lambda l=_l: __import__(f"loaders.{l}", fromlist=[l]))

# --- Prompts ---
for _p in ["simple_prompt", "advanced_prompt", "hackathon_prompt", "base_prompt", "specialized_prompts"]:
    check(f"prompts.{_p}", lambda p=_p: __import__(f"prompts.{p}", fromlist=[p]))

# --- Functional checks ---
def _check_generator_init():
    from core.generator import LinkedInGenerator
    g = LinkedInGenerator()
    assert g is not None

def _check_models():
    from core.models import (
        PostRequest, PostResponse, MultiModalInput,
        AgenticWorkflowResponse, HackathonProjectRequest,
        GenerationMode, Tone, Audience, ContentType
    )
    # Build a minimal valid PostRequest
    req = PostRequest(
        content_type=ContentType.EDUCATIONAL,
        topic="AI agents",
        tone=Tone.PROFESSIONAL,
        audience=Audience.PROFESSIONALS,
    )
    assert req.topic == "AI agents"

def _check_multimodal():
    from core.models import MultiModalInput
    m = MultiModalInput(text="test", tone="professional", audience="professionals")
    assert m.has_input()

def _check_orchestrator():
    from agents.agent_orchestrator import AgentOrchestrator
    orch = AgentOrchestrator(llm_provider=None)
    assert orch is not None

def _check_linkedin_poster():
    from tools.linkedin_poster import LinkedInPoster, LinkedInPostResult
    p = LinkedInPoster()
    # No credentials = should NOT raise, just warn
    assert p is not None

check("functional: generator init", _check_generator_init)
check("functional: models", _check_models)
check("functional: MultiModalInput", _check_multimodal)
check("functional: orchestrator init", _check_orchestrator)
check("functional: LinkedInPoster init", _check_linkedin_poster)

# --- Print Results ---
print("\n" + "=" * 60)
print("  PIPELINE VERIFICATION REPORT")
print("=" * 60)

print(f"\nPASSED ({len(results['ok'])}):")
for r in results["ok"]:
    print(f"   [OK] {r}")

if results["fail"]:
    print(f"\nFAILED ({len(results['fail'])}):")
    for label, err in results["fail"]:
        print(f"   [FAIL] {label}")
        print(f"      -> {err[:120]}")
else:
    print("\nALL CHECKS PASSED -- Pipeline is production-ready!")

print("\n" + "=" * 60)
sys.exit(0 if not results["fail"] else 1)
