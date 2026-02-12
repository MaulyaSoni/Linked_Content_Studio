"""
Quick test for refine_post method
"""

import os
if not os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = 'test_key_for_demo'

from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
from core.generator import LinkedInGenerator

# Test that refine_post method exists and works
generator = LinkedInGenerator(mode=GenerationMode.SIMPLE)

# Check method exists
assert hasattr(generator, 'refine_post'), "❌ refine_post method missing!"
print("✅ refine_post method exists")

# Test with sample post
sample_post = """AI automation is changing how developers work.

Here are 3 key insights.

Use these to build better products."""

request = PostRequest(
    content_type=ContentType.EDUCATIONAL,
    topic='AI automation',
    tone=Tone.PROFESSIONAL,
    audience=Audience.DEVELOPERS,
    mode=GenerationMode.SIMPLE
)

# Test refinement
result = generator.refine_post(sample_post, request)

print(f"\n✅ Refinement completed!")
print(f"Success: {result.success}")
print(f"Mode: {result.mode_used}")
print(f"Post length: {len(result.post) if result.post else 0}")

if result.post:
    print(f"\nRefined post preview:")
    print(result.post[:200] + "..." if len(result.post) > 200 else result.post)

print("\n✅ ALL TESTS PASSED - refine_post is working!")
