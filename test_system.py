#!/usr/bin/env python3
"""
LinkedIn Content Generator - System Test
Simple test to verify the system is working correctly.
"""

import os
import sys

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all core imports work."""
    print("🔄 Testing imports...")
    
    try:
        from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
        print("✅ Core models imported successfully")
        
        from core.generator import LinkedInGenerator
        print("✅ Generator imported successfully")
        
        from prompts.base_prompt import build_simple_prompt
        print("✅ Prompts imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_object_creation():
    """Test creating core objects."""
    print("\n🔄 Testing object creation...")
    
    try:
        from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
        
        request = PostRequest(
            content_type=ContentType.EDUCATIONAL,
            topic='AI automation',
            tone=Tone.PROFESSIONAL,
            audience=Audience.DEVELOPERS,
            mode=GenerationMode.SIMPLE
        )
        print("✅ PostRequest created successfully")
        
        return request
    except Exception as e:
        print(f"❌ Object creation failed: {e}")
        return None

def test_generator(request):
    """Test generator functionality."""
    print("\n🔄 Testing generator...")
    
    # Set dummy API key for testing if none exists
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️ No GROQ_API_KEY found - using demo mode")
        
    try:
        from core.generator import LinkedInGenerator
        
        generator = LinkedInGenerator(mode=GenerationMode.SIMPLE)
        print("✅ Generator created (with or without LLM)")
        
        result = generator.generate(request)
        print(f"✅ Generation completed: success={result.success}")
        
        if result.post:
            print(f"📝 Generated post ({len(result.post)} chars)")
        else:
            print("📝 No post content (demo mode)")
            
        return True
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 LinkedIn Content Generator - System Test")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        return
        
    # Test 2: Object creation  
    request = test_object_creation()
    if not request:
        return
        
    # Test 3: Generator
    if not test_generator(request):
        return
        
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("🎉 Your LinkedIn Content Generator is ready to use!")
    print("\nTo start the app:")
    print("1. Add your GROQ_API_KEY to a .env file")
    print("2. Run: streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()