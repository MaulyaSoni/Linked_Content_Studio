"""
Test Enhanced Prompts Integration
==================================
Verify that the generator now uses the enhanced PromptBuilder from core/prompts.py
"""

import os
import sys

# Setup environment
if not os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = 'test_key_for_demo'

from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
from core.prompts import PromptBuilder

print("=" * 70)
print("🧪 ENHANCED PROMPTS INTEGRATION TEST")
print("=" * 70)

# Test 1: Verify PromptBuilder.build_simple_prompt works
print("\n1️⃣  TEST: PromptBuilder.build_simple_prompt()")
print("-" * 70)

request_simple = PostRequest(
    content_type=ContentType.EDUCATIONAL,
    topic="Building a successful AI startup",
    tone=Tone.PROFESSIONAL,
    audience=Audience.FOUNDERS,
    mode=GenerationMode.SIMPLE
)

try:
    prompt_simple = PromptBuilder.build_simple_prompt(request_simple)
    
    # Verify enhanced features are present
    checks = [
        ("Has 5-section formula", "SECTION 1 - THE HOOK" in prompt_simple),
        ("Has psychology formula", "CRITICAL: You must follow this exact psychology formula" in prompt_simple),
        ("Has engagement optimization", "ENGAGEMENT OPTIMIZATION" in prompt_simple),
        ("Has forbidden patterns", "FORBIDDEN PATTERNS" in prompt_simple),
        ("Has tone rules", "TONE RULES" in prompt_simple),
        ("Has audience rules", "AUDIENCE RULES" in prompt_simple),
        ("No AI phrases banned", "feel like AI" in prompt_simple.lower() or "stop scrolling" in prompt_simple.lower()),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ SIMPLE prompt test PASSED - All enhanced features present!")
    else:
        print("\n❌ SIMPLE prompt test FAILED - Some features missing")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Verify PromptBuilder.build_advanced_prompt works
print("\n\n2️⃣  TEST: PromptBuilder.build_advanced_prompt()")
print("-" * 70)

request_advanced = PostRequest(
    content_type=ContentType.GITHUB_SHOWCASE,
    github_url="https://github.com/example/project",
    topic="AI project showcase",
    tone=Tone.BOLD,
    audience=Audience.DEVELOPERS,
    mode=GenerationMode.ADVANCED
)

mock_context = """
# Example AI Project

This is a cutting-edge AI application built with:
- Python 3.11
- FastAPI for backend
- React for frontend
- OpenAI GPT-4 integration

Features:
- Real-time AI responses
- 95% accuracy on benchmarks
- Handles 10k requests/day
"""

mock_sources = ["README.md", "docs/architecture.md", "package.json"]

try:
    prompt_advanced = PromptBuilder.build_advanced_prompt(
        request=request_advanced,
        context=mock_context,
        context_sources=mock_sources
    )
    
    # Verify enhanced features are present
    checks = [
        ("Has 7-section formula", "SECTION 1 - SPECIFIC HOOK" in prompt_advanced),
        ("Context injected", mock_context in prompt_advanced),
        ("Sources included", "README.md" in prompt_advanced),
        ("Has credibility signals", "CREDIBILITY SIGNALS" in prompt_advanced),
        ("Has authenticity rules", "AUTHENTICITY RULES" in prompt_advanced),
        ("Has your mission", "YOUR MISSION" in prompt_advanced),
        ("GitHub URL present", request_advanced.github_url in prompt_advanced),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ ADVANCED prompt test PASSED - All enhanced features present!")
    else:
        print("\n❌ ADVANCED prompt test FAILED - Some features missing")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Verify Generator imports correctly
print("\n\n3️⃣  TEST: Generator imports PromptBuilder correctly")
print("-" * 70)

try:
    from core.generator import LinkedInGenerator
    import inspect
    
    # Check if PromptBuilder is imported in generator module
    gen_source = inspect.getsource(LinkedInGenerator)
    
    checks = [
        ("PromptBuilder imported", "PromptBuilder" in gen_source),
        ("build_simple_prompt used", "build_simple_prompt" in gen_source),
        ("build_advanced_prompt used", "build_advanced_prompt" in gen_source),
        ("Old import removed", "from prompts.simple_prompt import build_prompt" not in gen_source),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ Generator integration test PASSED!")
    else:
        print("\n❌ Generator integration test FAILED")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Full integration test (if LLM available)
print("\n\n4️⃣  TEST: Full Generator Integration (Optional)")
print("-" * 70)

if os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY') != 'test_key_for_demo':
    try:
        from core.generator import LinkedInGenerator
        
        generator = LinkedInGenerator()
        
        # Test simple mode
        print("Testing SIMPLE mode generation...")
        simple_request = PostRequest(
            content_type=ContentType.LEARNING_SHARE,
            topic="How I learned to build with AI",
            tone=Tone.CASUAL,
            audience=Audience.DEVELOPERS,
            mode=GenerationMode.SIMPLE,
            max_length=1200
        )
        
        result = generator.generate(simple_request)
        
        if result.success and result.post:
            print(f"✅ Simple mode generation successful!")
            print(f"   Generated {len(result.post)} characters")
            print(f"   Mode used: {result.mode_used}")
            print(f"   First 150 chars: {result.post[:150]}...")
        else:
            print(f"❌ Simple mode generation failed: {result.error_message}")
            
    except Exception as e:
        print(f"⚠️  Integration test skipped: {e}")
else:
    print("⚠️  Skipped - No real GROQ_API_KEY found (requires real API key)")

print("\n" + "=" * 70)
print("🎯 ENHANCED PROMPTS TEST COMPLETE")
print("=" * 70)
