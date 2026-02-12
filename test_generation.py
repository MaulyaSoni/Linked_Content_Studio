#!/usr/bin/env python3
"""
Quick test to verify the generation system is working correctly.
"""

import os
import sys

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Test the generation system."""
    print("=" * 60)
    print("🧪 Testing LinkedIn Content Generator")
    print("=" * 60)
    
    # Import models
    from core.models import PostRequest, GenerationMode, Tone, ContentType, Audience
    
    # Create a test request
    print("\n1️⃣ Creating test request...")
    request = PostRequest(
        content_type=ContentType.EDUCATIONAL,
        topic='Building AI automation tools',
        tone=Tone.PROFESSIONAL,
        audience=Audience.DEVELOPERS,
        mode=GenerationMode.SIMPLE
    )
    print("✅ Request created successfully")
    
    # Initialize generator
    print("\n2️⃣ Initializing generator...")
    from core.generator import LinkedInGenerator
    generator = LinkedInGenerator(mode=GenerationMode.SIMPLE)
    print("✅ Generator initialized")
    
    # Test generation
    print("\n3️⃣ Testing generation...")
    result = generator.generate(request)
    
    print("\n" + "=" * 60)
    print("📊 GENERATION RESULTS")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Mode Used: {result.mode_used}")
    print(f"Post Length: {len(result.post)} characters")
    print(f"Tokens Used: {result.tokens_used}")
    
    if result.post:
        print("\n📝 Generated Post:")
        print("-" * 60)
        print(result.post)
        print("-" * 60)
        
        if result.hashtags:
            print(f"\n🏷️ Hashtags: {result.hashtags}")
        
        if result.caption:
            print(f"\n📄 Caption: {result.caption}")
    else:
        print("\n⚠️ No content generated")
        if result.error_message:
            print(f"Error: {result.error_message}")
    
    print("\n" + "=" * 60)
    if result.success:
        print("✅ GENERATION TEST PASSED!")
    else:
        print("❌ GENERATION TEST FAILED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
