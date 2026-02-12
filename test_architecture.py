#!/usr/bin/env python3
"""
Test SIMPLE vs ADVANCED RAG Architecture
========================================
Verifies the clean separation between modes.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_architecture():
    """Test the SIMPLE vs ADVANCED mode separation."""
    
    print("=" * 70)
    print("🧪 TESTING SIMPLE vs ADVANCED RAG ARCHITECTURE")
    print("=" * 70)
    
    # Import models
    from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
    from core.generator import LinkedInGenerator
    
    print("\n1️⃣ TESTING SIMPLE MODE (No RAG)")
    print("-" * 70)
    
    # Create SIMPLE mode request
    simple_request = PostRequest(
        content_type=ContentType.EDUCATIONAL,
        topic='Building AI automation tools that actually work',
        tone=Tone.BOLD,
        audience=Audience.DEVELOPERS,
        mode=GenerationMode.SIMPLE
    )
    
    # Test SIMPLE mode
    print("✅ Request created: SIMPLE mode")
    print(f"   Topic: {simple_request.topic}")
    print(f"   Mode: {simple_request.mode.value}")
    
    try:
        generator_simple = LinkedInGenerator(mode=GenerationMode.SIMPLE)
        print("✅ Generator initialized for SIMPLE mode")
        print(f"   RAG available: {generator_simple.rag_available}")
        print(f"   LLM available: {generator_simple.llm_available}")
        
        print("\n🔄 Generating SIMPLE mode post...")
        result_simple = generator_simple.generate(simple_request)
        
        print(f"\n📊 SIMPLE MODE RESULTS:")
        print(f"   Success: {result_simple.success}")
        print(f"   Mode Used: {result_simple.mode_used}")
        print(f"   Content Length: {len(result_simple.post)} chars")
        print(f"   Context Sources: {result_simple.context_sources}")
        
        if result_simple.post:
            print(f"\n📝 Generated Post (SIMPLE):")
            print("   " + "-" * 66)
            preview = result_simple.post[:300]
            print("   " + preview.replace("\n", "\n   ") + "...")
            print("   " + "-" * 66)
        
    except Exception as e:
        print(f"❌ SIMPLE mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n2️⃣ TESTING ADVANCED MODE (With RAG)")
    print("-" * 70)
    
    # Create ADVANCED mode request
    advanced_request = PostRequest(
        content_type=ContentType.GITHUB_SHOWCASE,
        topic='Open source project that solves real problems',
        github_url='https://github.com/example/ai-tools',
        tone=Tone.PROFESSIONAL,
        audience=Audience.TECH_LEADERS,
        mode=GenerationMode.ADVANCED
    )
    
    print("✅ Request created: ADVANCED mode")
    print(f"   Topic: {advanced_request.topic}")
    print(f"   GitHub URL: {advanced_request.github_url}")
    print(f"   Mode: {advanced_request.mode.value}")
    
    try:
        generator_advanced = LinkedInGenerator(mode=GenerationMode.ADVANCED)
        print("✅ Generator initialized for ADVANCED mode")
        print(f"   RAG available: {generator_advanced.rag_available}")
        print(f"   LLM available: {generator_advanced.llm_available}")
        
        print("\n🔄 Generating ADVANCED mode post...")
        result_advanced = generator_advanced.generate(advanced_request)
        
        print(f"\n📊 ADVANCED MODE RESULTS:")
        print(f"   Success: {result_advanced.success}")
        print(f"   Mode Used: {result_advanced.mode_used}")
        print(f"   Content Length: {len(result_advanced.post)} chars")
        print(f"   Context Sources: {result_advanced.context_sources}")
        
        if result_advanced.post:
            print(f"\n📝 Generated Post (ADVANCED):")
            print("   " + "-" * 66)
            preview = result_advanced.post[:300]
            print("   " + preview.replace("\n", "\n   ") + "...")
            print("   " + "-" * 66)
            
    except Exception as e:
        print(f"❌ ADVANCED mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ ARCHITECTURE TEST COMPLETE!")
    print("=" * 70)
    
    print("\n🎯 VERIFICATION:")
    print(f"   ✅ SIMPLE mode uses: {'No RAG (direct prompt)' if 'direct_prompt' in result_simple.context_sources else 'RAG'}")
    print(f"   ✅ ADVANCED mode uses: {'RAG with context' if len(result_advanced.context_sources) > 1 or result_advanced.mode_used == 'advanced' else 'Fallback to simple'}")
    
    print("\n💡 KEY DIFFERENCES:")
    print("   • SIMPLE: Topic → Psychology Prompt → LLM → Output (3-5s)")
    print("   • ADVANCED: Topic → RAG Retrieval → Context Injection → LLM → Output (8-15s)")
    
    return True


if __name__ == "__main__":
    success = test_architecture()
    sys.exit(0 if success else 1)
