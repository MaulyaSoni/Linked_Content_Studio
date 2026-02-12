# ============================================================================
# EXPORT FUNCTIONALITY TEST SCRIPT
# ============================================================================
# This script tests all four export options to ensure they work correctly

from utils.export_handler import ExportHandler
import json
from datetime import datetime

def test_export_functions():
    """Test all export functions with sample data"""
    
    # Sample post data (similar to what the app generates)
    test_post_data = {
        "post": """🚀 Just launched our new AI-powered LinkedIn content generator!

This tool leverages advanced language models to create engaging, professional posts tailored to your GitHub projects. 

Key features:
✅ Smart content analysis from GitHub repos
✅ Multiple writing styles (Professional, Casual, Technical)
✅ Automatic hashtag generation
✅ Safety checks to prevent hallucinations
✅ Export to multiple formats

The future of content creation is here! 🔥""",
        "hashtags": "#AI #MachineLearning #LinkedIn #ContentCreation #GitHub #LangChain #Automation #SocialMedia #TechInnovation",
        "caption": "Watch how our AI tool transforms a GitHub repository into engaging LinkedIn content in seconds!",
        "style": "Professional",
        "tone": "Enthusiastic",
        "stats": {
            "word_count": 89,
            "char_count": 587
        },
        "quality_score": "92%"
    }
    
    print("=" * 60)
    print("🧪 TESTING EXPORT FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: LinkedIn Export
    print("\n1️⃣ Testing LinkedIn Export...")
    try:
        linkedin_export = ExportHandler.export_for_linkedin(test_post_data)
        print(f"✅ LinkedIn Export - SUCCESS")
        print(f"   Length: {len(linkedin_export)} characters")
        print(f"   Preview: {linkedin_export[:100]}...")
        
        # Save to file for verification
        with open("test_linkedin_export.txt", "w", encoding="utf-8") as f:
            f.write(linkedin_export)
        print("   📁 Saved as: test_linkedin_export.txt")
            
    except Exception as e:
        print(f"❌ LinkedIn Export - FAILED: {e}")
    
    # Test 2: Markdown Export
    print("\n2️⃣ Testing Markdown Export...")
    try:
        md_export = ExportHandler.export_for_markdown(test_post_data, "AI Content Generator")
        print(f"✅ Markdown Export - SUCCESS")
        print(f"   Length: {len(md_export)} characters")
        print(f"   Preview: {md_export[:150].replace(chr(10), ' ')}...")
        
        # Save to file for verification
        filename = f"test_linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_export)
        print(f"   📁 Saved as: {filename}")
            
    except Exception as e:
        print(f"❌ Markdown Export - FAILED: {e}")
    
    # Test 3: Notion Export
    print("\n3️⃣ Testing Notion Export...")
    try:
        notion_export = ExportHandler.export_for_notion(test_post_data)
        notion_json = json.dumps(notion_export, indent=2)
        print(f"✅ Notion Export - SUCCESS")
        print(f"   JSON Length: {len(notion_json)} characters")
        print(f"   Fields: {list(notion_export.keys())}")
        
        # Save to file for verification
        filename = f"test_linkedin_notion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(notion_json)
        print(f"   📁 Saved as: {filename}")
            
    except Exception as e:
        print(f"❌ Notion Export - FAILED: {e}")
    
    # Test 4: Buffer Export
    print("\n4️⃣ Testing Buffer Export...")
    try:
        buffer_export = ExportHandler.export_for_scheduling(test_post_data, "buffer")
        buffer_json = json.dumps(buffer_export, indent=2)
        print(f"✅ Buffer Export - SUCCESS")
        print(f"   JSON Length: {len(buffer_json)} characters")
        print(f"   Fields: {list(buffer_export.keys())}")
        
        # Save to file for verification
        filename = f"test_linkedin_buffer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(buffer_json)
        print(f"   📁 Saved as: {filename}")
            
    except Exception as e:
        print(f"❌ Buffer Export - FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 EXPORT FUNCTIONALITY TEST COMPLETE!")
    print("=" * 60)
    
    # Instructions for user
    print("\n📋 NEXT STEPS:")
    print("1. Open the Streamlit app: http://localhost:8503")
    print("2. Generate a LinkedIn post using any GitHub repo")
    print("3. Scroll down to the '📤 Export Options' section")
    print("4. Test all four export buttons:")
    print("   • 📋 Copy Ready - Shows formatted text")
    print("   • 📝 Save as MD - Downloads markdown file")
    print("   • 💡 Export to Notion - Downloads JSON file")  
    print("   • 📅 Buffer.com Format - Downloads JSON file")
    print("\n✅ All export functions should work without errors!")

if __name__ == "__main__":
    test_export_functions()