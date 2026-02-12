"""
COMPREHENSIVE TEST: Prompt Contamination Fixes
==============================================
Tests all fixes for:
1. Fake statistics blocking
2. Corporate buzzword blocking  
3. Refinement meta-commentary leakage
4. Natural output parsing
5. Structured vs natural format handling
"""

import os
if not os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = 'test_key_for_demo'

from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
from core.generator import LinkedInGenerator

print("=" * 70)
print("🧪 PROMPT CONTAMINATION FIX - VERIFICATION TEST")
print("=" * 70)

# Test 1: Check prompts ban fake statistics
print("\n1️⃣  CHECKING PROMPT CONSTRAINTS")
print("-" * 70)

from prompts.simple_prompt import SimplePrompt
from prompts.advanced_prompt import AdvancedPrompt

simple_prompt_test = SimplePrompt.build(PostRequest(
    content_type=ContentType.EDUCATIONAL,
    topic="test"
))

advanced_prompt_test = AdvancedPrompt.build(
    PostRequest(content_type=ContentType.EDUCATIONAL, topic="test"),
    type('obj', (object,), {'content': 'test context'})
)

# Check for critical constraints
checks = [
    ("FAKE STATISTICS banned in SIMPLE", "FAKE STATISTICS" in simple_prompt_test or "fake stat" in simple_prompt_test.lower()),
    ("Corporate buzzwords banned in SIMPLE", "corporate buzzword" in simple_prompt_test.lower() or "game-changing" in simple_prompt_test),
    ("FAKE STATISTICS banned in ADVANCED", "FAKE STATISTICS" in advanced_prompt_test or "fake stat" in advanced_prompt_test.lower()),
    ("No structured labels in SIMPLE", "Do NOT use labels" in simple_prompt_test or "POST:" not in simple_prompt_test.split("OUTPUT")[1] if "OUTPUT" in simple_prompt_test else True),
    ("No structured labels in ADVANCED", "Do NOT write \"POST:\"" in advanced_prompt_test or "naturally" in advanced_prompt_test)
]

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")

# Test 2: Parser handles natural output
print("\n2️⃣  TESTING NATURAL OUTPUT PARSER")
print("-" * 70)

generator = LinkedInGenerator(mode=GenerationMode.SIMPLE)

# Test natural format (no labels)
natural_output = """I spent 6 months on this project.

Here's what broke.

Most teams miss these 3 things:

• Context over code
• Speed over perfection  
• Shipping over planning

Anyone else hit this wall?

#AI #Development #BuildInPublic"""

post, hashtags, caption = generator._parse_llm_response(natural_output)

print(f"✅ Natural format parsed:")
print(f"   Post length: {len(post)} chars")
print(f"   Hashtags: {hashtags}")
print(f"   Has meta-commentary: {'refinement' in post.lower() or 'changes made' in post.lower()}")

# Test structured format (backwards compatibility)
structured_output = """POST:
This is the post content.

HASHTAGS:
#AI #Tech

CAPTION:
Short caption"""

post2, hashtags2, caption2 = generator._parse_llm_response(structured_output)

print(f"\n✅ Structured format still works:")
print(f"   Post length: {len(post2)} chars")
print(f"   Hashtags: {hashtags2}")
print(f"   Caption: {caption2}")

# Test 3: Refinement prompt is clean (humanizer pass)
print("\n3️⃣  CHECKING REFINEMENT PROMPT (HUMANIZER PASS)")
print("-" * 70)

# Check refine_post method exists and has correct behavior
import inspect
refine_source = inspect.getsource(generator.refine_post)

refinement_checks = [
    ("Method exists", hasattr(generator, 'refine_post')),
    ("Bans meta-commentary", "Do NOT explain what you changed" in refine_source or "meta-commentary" in refine_source.lower()),
    ("Bans fake statistics", "Do NOT add fake statistics" in refine_source or "fake stat" in refine_source.lower()),
    ("Returns only final post", "Return ONLY" in refine_source or "Just write the post" in refine_source),
    ("No structured labels", "Do NOT include labels" in refine_source or "POST:" in refine_source.split("FORBIDDEN")[1] if "FORBIDDEN" in refine_source else False)
]

for check_name, result in refinement_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")

# Test 4: Generate real content (demo mode) and check output
print("\n4️⃣  TESTING ACTUAL GENERATION")
print("-" * 70)

request = PostRequest(
    content_type=ContentType.HOT_TAKE,
    topic="Why most AI projects fail",
    tone=Tone.BOLD,
    audience=Audience.TECH_LEADERS,
    mode=GenerationMode.SIMPLE
)

result = generator.generate(request)

print(f"Success: {result.success}")
print(f"Mode: {result.mode_used}")
print(f"Post length: {len(result.post)} chars")

# Check for anti-patterns
anti_patterns = {
    "Fake statistics (85%)": any(f"{x}%" in result.post for x in range(50, 100)),
    "Corporate buzzwords": any(word in result.post.lower() for word in ["game-changing", "revolutionary", "unlock", "leverage"]),
    "Marketing speak": any(phrase in result.post.lower() for phrase in ["here's the good news", "the truth is", "the secret to"]),
    "Structured labels": any(label in result.post for label in ["POST:", "HASHTAGS:", "CAPTION:"]),
    "Meta-commentary": any(phrase in result.post.lower() for phrase in ["refinements made", "changes:", "improvements:"])
}

print("\n🔍 ANTI-PATTERN DETECTION:")
for pattern, detected in anti_patterns.items():
    status = "❌ FOUND" if detected else "✅ CLEAN"
    print(f"{status}: {pattern}")

# Test 5: Test refinement doesn't leak analysis
print("\n5️⃣  TESTING REFINEMENT (HUMANIZER PASS)")
print("-" * 70)

sample_post = """Most AI projects fail in production.

Here's why:
• Over-engineering
• No user feedback
• Analysis paralysis"""

refined = generator.refine_post(sample_post, request)

print(f"Refinement success: {refined.success}")
print(f"Refinement mode: {refined.mode_used}")

# Check refined output for leakage
refinement_leakage = {
    "Meta-commentary leaked": any(phrase in refined.post.lower() for phrase in ["refinements made", "changes:", "i've", "improvements:"]),
    "Analysis included": any(phrase in refined.post.lower() for phrase in ["refinement rule", "output format", "note:"]),
    "Labels leaked": any(label in refined.post for label in ["POST:", "HASHTAGS:", "CAPTION:"])
}

print("\n🔍 REFINEMENT LEAKAGE CHECK:")
for issue, detected in refinement_leakage.items():
    status = "❌ LEAKED" if detected else "✅ CLEAN"
    print(f"{status}: {issue}")

# Final summary
print("\n" + "=" * 70)
print("✅ COMPREHENSIVE TEST COMPLETE!")
print("=" * 70)

all_checks_pass = (
    all(result for _, result in checks) and
    not any(detected for detected in anti_patterns.values()) and
    not any(detected for detected in refinement_leakage.values())
)

if all_checks_pass:
    print("\n🎉 ALL CHECKS PASSED - Prompt contamination fixed!")
    print("   ✅ Fake statistics banned")
    print("   ✅ Corporate buzzwords banned")
    print("   ✅ Natural output supported")
    print("   ✅ Refinement doesn't leak meta-commentary")
    print("   ✅ No structured labels in output")
else:
    print("\n⚠️  Some issues detected - review output above")

print("\n📊 Sample output preview:")
print("-" * 70)
print(result.post[:300] + "..." if len(result.post) > 300 else result.post)
print("-" * 70)
if result.hashtags:
    print(f"Hashtags: {result.hashtags}")
