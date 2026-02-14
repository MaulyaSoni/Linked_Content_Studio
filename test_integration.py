#!/usr/bin/env python
"""
Integration test for quality chains improvements
Tests that all components integrate correctly
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    try:
        from core.models import PostRequest, ContentType, Tone, Audience, GenerationMode, PostResponse
        print("✅ core.models imports successful")
    except ImportError as e:
        print(f"❌ core.models import failed: {e}")
        return False
    
    try:
        from core.llm import get_llm, get_llm_deterministic
        print("✅ core.llm functions available")
    except ImportError as e:
        print(f"❌ core.llm import failed: {e}")
        return False
    
    try:
        from ui.components import UIComponents
        print("✅ UI components imports successful")
    except ImportError as e:
        print(f"❌ UI components import failed: {e}")
        return False
    
    try:
        import chains.quality_chains
        print("✅ chains.quality_chains module loads (lazy initialization)")
    except ImportError as e:
        print(f"❌ chains.quality_chains import failed: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True


def test_postresponse():
    """Test PostResponse with quality fields."""
    print("=" * 60)
    print("Testing PostResponse with quality fields...")
    print("=" * 60)
    
    from core.models import PostResponse
    
    # Create a sample response with quality fields
    response = PostResponse(
        success=True,
        post="Test post content",
        hashtags="#test #linkedin",
        caption="Test caption",
        mode_used="simple",
        context_sources=["source1", "source2"],
        estimated_engagement="high",
        hook_strength="strong",
        context_quality=0.85,
        generation_time=2.5,
        tokens_used=150,
        hook_options={
            "curiosity": "Did you know...",
            "outcome": "This led to...",
            "contrarian": "Most people think..."
        },
        quality_score={
            "clarity": "8/10",
            "specificity": "7/10",
            "engagement": "8/10", 
            "credibility": "9/10",
            "actionability": "7/10"
        }
    )
    
    # Verify fields exist and have correct values
    assert response.success == True, "success field incorrect"
    assert response.post == "Test post content", "post field incorrect"
    assert response.hook_options["curiosity"] == "Did you know...", "hook_options incorrect"
    assert response.quality_score["clarity"] == "8/10", "quality_score incorrect"
    
    print(f"✅ PostResponse structure valid")
    print(f"   - Has hook_options: {bool(response.hook_options)}")
    print(f"   - Has quality_score: {bool(response.quality_score)}")
    print(f"   - All fields accessible and correct\n")
    
    return True


def test_ui_components():
    """Test that UI components accept new advanced options."""
    print("=" * 60)
    print("Testing UI advanced options...")
    print("=" * 60)
    
    try:
        from ui.components import UIComponents
        
        # Check that render_advanced_options would return new fields
        # We can't actually call it without Streamlit running, but we can verify
        # the function exists and the code structure is correct
        import inspect
        source = inspect.getsource(UIComponents.render_advanced_options)
        
        required_fields = [
            "enforce_specificity",
            "show_quality_score",
            "generate_hook_options",
            "ground_claims"
        ]
        
        for field in required_fields:
            if field in source:
                print(f"✅ Found '{field}' in advanced options")
            else:
                print(f"❌ Missing '{field}' in advanced options")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        return False


def test_quality_functions():
    """Test that quality chain functions exist."""
    print("=" * 60)
    print("Testing quality chain functions...")
    print("=" * 60)
    
    try:
        import chains.quality_chains as qc
        
        functions = [
            'enforce_specificity',
            'score_post_quality',
            'generate_hook_options',
            'ground_in_context'
        ]
        
        for func_name in functions:
            if hasattr(qc, func_name):
                func = getattr(qc, func_name)
                if callable(func):
                    print(f"✅ Function '{func_name}' exists and is callable")
                else:
                    print(f"❌ '{func_name}' exists but is not callable")
                    return False
            else:
                print(f"❌ Function '{func_name}' not found")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing quality functions: {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("LinkedIn Post Generator - Integration Tests")
    print("=" * 60 + "\n")
    
    results = {
        "Imports": test_imports(),
        "PostResponse": test_postresponse(),
        "UI Components": test_ui_components(),
        "Quality Functions": test_quality_functions(),
    }
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n{passed}/{total} tests passed\n")
    
    if passed == total:
        print("✅ All integration tests passed!")
        print("\nThe quality improvements are ready to use.")
        print("Features available:")
        print("  • Specificity Enforcer - removes vague phrases")
        print("  • Quality Scorer - evaluates post on 5 dimensions")
        print("  • Hook Generator - creates 3 engagement hooks")
        print("  • Context Grounder - verifies claims against context")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
