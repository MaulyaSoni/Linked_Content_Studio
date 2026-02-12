"""
Demo Script - Testing the README Fallback Retriever
=====================================================

This script demonstrates how the fallback retriever works with different scenarios.
Run this to understand the production-ready graceful degradation flow.

Usage:
    python test_fallback_retriever.py
"""

from rag.readme_fallback_retriever import ReadmeFallbackRetriever
from utils.exceptions import (
    ReadmeNotFoundException,
    InsufficientRepositoryDataException,
    RepositoryAccessException
)


def demo_scenario_1():
    """Scenario 1: Repository WITH README"""
    print("\n" + "="*70)
    print("📊 SCENARIO 1: Repository WITH README")
    print("="*70)
    print("\nRepo: https://github.com/pallets/flask")
    print("Expected: Use README (Best quality)\n")
    
    try:
        retriever = ReadmeFallbackRetriever("https://github.com/pallets/flask")
        docs, status = retriever.retrieve_context()
        
        print(f"✅ SUCCESS")
        print(f"   README Found: {status['readme_found']}")
        print(f"   Sources Used: {len(status['sources_used'])}")
        print(f"   Data Completeness: {status['data_completeness']}")
        print(f"\n   Transparency Message:")
        print(f"   {status.get('sources_used', [])}")
        
        return True
    
    except Exception as e:
        print(f"❌ {type(e).__name__}: {str(e)[:100]}")
        return False


def demo_scenario_2():
    """Scenario 2: Repository WITHOUT README (Fallback)"""
    print("\n" + "="*70)
    print("📊 SCENARIO 2: Repository WITHOUT README (Uses Fallback)")
    print("="*70)
    print("\nRepo: https://github.com/your-username/your-repo-without-readme")
    print("Expected: Degrade gracefully to metadata + structure + commits\n")
    
    print("⚠️  NOTE: This example uses a hypothetical repo")
    print("   In production, system will:")
    print("   1. Try README → ❌ Not found")
    print("   2. Load metadata → ✅ GitHub API info")
    print("   3. Analyze structure → ✅ File tree")
    print("   4. Get requirements → ✅ Tech stack")
    print("   5. Get commits → ✅ Activity")
    print("   6. Get issues → ✅ Problems being solved")
    print("\n   Result: Post generated from 5 sources (no hallucination)")


def demo_scenario_3():
    """Scenario 3: Private Repository (Error Handling)"""
    print("\n" + "="*70)
    print("📊 SCENARIO 3: Private Repository (Error Handling)")
    print("="*70)
    print("\nRepo: https://github.com/private-org/private-repo")
    print("Expected: Clear error message, not hallucination\n")
    
    try:
        retriever = ReadmeFallbackRetriever("https://github.com/private-org/private-repo")
        docs, status = retriever.retrieve_context()
    
    except RepositoryAccessException as e:
        print("✅ Correctly caught RepositoryAccessException:")
        print(f"   {str(e)[:150]}...")
        return True
    
    except Exception as e:
        print(f"⚠️  Exception: {type(e).__name__}")
        return False


def demo_error_categories():
    """Show the error handling strategy"""
    print("\n" + "="*70)
    print("🛡️  ERROR HANDLING CATEGORIES")
    print("="*70)
    
    print("\n1. RepositoryAccessException")
    print("   When: Cannot access repo (private, credentials, network)")
    print("   Action: STOP - Don't generate")
    print("   Message: Clear troubleshooting steps")
    
    print("\n2. InsufficientRepositoryDataException")
    print("   When: Repo exists but ALL sources are empty")
    print("   Action: STOP - Don't generate")
    print("   Message: Tell user what to add")
    
    print("\n3. ReadmeNotFoundException")
    print("   When: README missing but fallback sources available")
    print("   Action: Generate from fallback sources")
    print("   Message: Show user what was used")
    
    print("\n4. DataQualityWarning")
    print("   When: Data quality is low (< 50% completeness)")
    print("   Action: Generate but warn user")
    print("   Message: Recommend adding README")


def demo_transparency():
    """Show how transparency works"""
    print("\n" + "="*70)
    print("👁️  TRANSPARENCY IN ACTION")
    print("="*70)
    
    print("\nWhen README is found:")
    print("   UI Message: ✅ Post generated from README documentation")
    print("   Quality: HIGH")
    print("   User sees: This is based on official documentation")
    
    print("\nWhen README is missing but good fallback data:")
    print("   UI Message: ⚠️  README not found. Using repository intelligence:")
    print("             Sources: metadata, file_structure, requirements, commits")
    print("   Quality: MEDIUM-HIGH")
    print("   User sees: What data was actually used, not hallucination")
    
    print("\nExpanded details panel shows:")
    print("   • README Available: ✅/⚠️")
    print("   • Sources Used: 4 (metadata, structure, requirements, commits)")
    print("   • Data Quality: Medium")
    print("   • Reasoning: Why this set of sources")


def show_architecture():
    """Display the retrieval hierarchy"""
    print("\n" + "="*70)
    print("🧱 RETRIEVAL HIERARCHY")
    print("="*70)
    
    hierarchy = [
        ("1️⃣", "README.md", "Primary source", "Highest quality"),
        ("2️⃣", "Repository Metadata", "GitHub API", "High quality"),
        ("3️⃣", "File Structure", "Directory tree analysis", "Medium quality"),
        ("4️⃣", "Requirements", "Tech stack from requirements.txt", "High quality"),
        ("5️⃣", "Commit Messages", "Recent activity", "Medium quality"),
        ("6️⃣", "Issues & PRs", "Problems being solved", "Low quality"),
    ]
    
    for level, source, method, quality in hierarchy:
        print(f"\n{level} {source}")
        print(f"   Method: {method}")
        print(f"   Quality: {quality}")


def show_code_example():
    """Show how to use the API"""
    print("\n" + "="*70)
    print("💻 CODE EXAMPLE")
    print("="*70)
    
    code = '''
# Basic usage
from rag.readme_fallback_retriever import ReadmeFallbackRetriever

retriever = ReadmeFallbackRetriever("https://github.com/user/repo")
documents, status = retriever.retrieve_context()

# Check what was retrieved
if status["readme_found"]:
    print("✅ Using README")
else:
    print("⚠️ Using fallback sources:", status["sources_used"])

# Show transparency
print(retriever.get_transparency_message())

# Logging
print(f"Completeness: {status['data_completeness']}")
print(f"Sources: {status['sources_used']}")
    '''
    
    print(code)


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "README FALLBACK RETRIEVER - DEMO" + " "*21 + "║")
    print("║" + " "*12 + "Production-Ready Graceful Degradation" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    # Show architecture
    show_architecture()
    
    # Show error categories
    demo_error_categories()
    
    # Show transparency
    demo_transparency()
    
    # Show code example
    show_code_example()
    
    # Show scenarios (demos)
    print("\n" + "="*70)
    print("🧪 RUNNING DEMO SCENARIOS")
    print("="*70)
    
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    
    print("\n📚 For full documentation, see: FALLBACK_RETRIEVER_GUIDE.md")
    print("📝 For implementation details, see: rag/readme_fallback_retriever.py")
    print("🛡️  For error handling, see: utils/exceptions.py")
