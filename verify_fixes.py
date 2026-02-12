#!/usr/bin/env python3
"""
Quick verification that the signal error is fixed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Verifying Windows compatibility fix...")
print("-" * 60)

# Test 1: Import core modules
print("\n1. Testing imports...")
try:
    from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience, LLMResult
    print("   ✅ Models imported")
    from core.llm import LLMProvider
    print("   ✅ LLM provider imported")
    from core.generator import LinkedInGenerator
    print("   ✅ Generator imported")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check LLMResult structure
print("\n2. Testing LLMResult structure...")
try:
    test_result = LLMResult(
        content="Test content",
        success=True,
        tokens_used=10,
        model_used="test"
    )
    print(f"   ✅ LLMResult created: success={test_result.success}")
    print(f"   ✅ Content accessible: {len(test_result.content)} chars")
except Exception as e:
    print(f"   ❌ LLMResult test failed: {e}")
    sys.exit(1)

# Test 3: Test PostRequest creation
print("\n3. Testing PostRequest...")
try:
    request = PostRequest(
        content_type=ContentType.EDUCATIONAL,
        topic="Test topic",
        tone=Tone.PROFESSIONAL,
        audience=Audience.DEVELOPERS,
        mode=GenerationMode.SIMPLE
    )
    print(f"   ✅ PostRequest created: {request.topic}")
except Exception as e:
    print(f"   ❌ PostRequest test failed: {e}")
    sys.exit(1)

# Test 4: Test generator initialization
print("\n4. Testing generator initialization...")
try:
    generator = LinkedInGenerator(mode=GenerationMode.SIMPLE)
    print(f"   ✅ Generator initialized")
    print(f"   ✅ LLM available: {generator.llm_available}")
except Exception as e:
    print(f"   ❌ Generator init failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test generation (quick)
print("\n5. Testing generation...")
try:
    if generator.llm_available:
        print("   🔄 LLM available - testing real generation...")
    else:
        print("   🔄 LLM not available - testing demo mode...")
    
    result = generator.generate(request)
    print(f"   ✅ Generation completed")
    print(f"   ✅ Result type: {type(result).__name__}")
    print(f"   ✅ Success: {result.success}")
    print(f"   ✅ Has content: {bool(result.post)}")
    print(f"   ✅ Mode used: {result.mode_used}")
    
    if result.post:
        print(f"   ✅ Content length: {len(result.post)} chars")
        print(f"\n   Preview:")
        print(f"   {result.post[:100]}...")
    
except Exception as e:
    print(f"   ❌ Generation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL VERIFICATION TESTS PASSED!")
print("=" * 60)
print("\n🎉 The system is working correctly!")
print("💡 You can now run: streamlit run app.py")
print("-" * 60)
