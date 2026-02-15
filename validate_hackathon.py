"""
Quick validation script - checks if hackathon feature is properly implemented
WITHOUT making any actual API calls
"""

import sys
import os

print("=" * 70)
print("HACKATHON FEATURE VALIDATION (NO API CALLS)")
print("=" * 70)

# Track results
results = []

# Test 1: Import models
print("\n1️⃣ Testing HackathonProjectRequest import...")
try:
    from core.models import HackathonProjectRequest, HackathonAchievement, HackathonType, HackathonPostResponse
    print("   ✅ Models imported successfully")
    results.append(("Models Import", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("Models Import", False))

# Test 2: Import prompt builder
print("\n2️⃣ Testing HackathonPromptBuilder import...")
try:
    from prompts.hackathon_prompt import HackathonPromptBuilder
    print("   ✅ Prompt builder imported successfully")
    results.append(("Prompt Builder Import", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("Prompt Builder Import", False))

# Test 3: Check generator has hackathon methods
print("\n3️⃣ Testing LinkedInGenerator has hackathon methods...")
try:
    from core.generator import LinkedInGenerator
    assert hasattr(LinkedInGenerator, 'generate_hackathon_post'), "generate_hackathon_post method not found"
    assert hasattr(LinkedInGenerator, '_generate_hackathon_hashtags'), "_generate_hackathon_hashtags method not found"
    print("   ✅ Generator has hackathon methods")
    results.append(("Generator Methods", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("Generator Methods", False))

# Test 4: Check UI component
print("\n4️⃣ Testing render_hackathon_section function...")
try:
    from ui.components import render_hackathon_section
    print("   ✅ UI component imported successfully")
    results.append(("UI Component", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("UI Component", False))

# Test 5: Create and validate a hackathon request (no API call)
print("\n5️⃣ Testing HackathonProjectRequest creation and validation...")
try:
    from core.models import HackathonProjectRequest, HackathonAchievement, HackathonType
    
    request = HackathonProjectRequest(
        hackathon_name="Test Hackathon",
        project_name="Test Project",
        team_size=4,
        problem_statement="Test problem statement",
        solution_description="Test solution",
        tech_stack=["Python", "React"],
        key_features=["Feature 1", "Feature 2"],
        completion_time_hours=24,
        achievement=HackathonAchievement.PARTICIPANT,
        personal_journey="Test journey",
        key_learnings=["Learning 1", "Learning 2"],
        hackathon_type=HackathonType.GENERAL
    )
    
    # Validate
    request.validate()
    
    # Check enums
    assert request.achievement == HackathonAchievement.PARTICIPANT
    assert request.hackathon_type == HackathonType.GENERAL
    
    print("   ✅ Request creation and validation working")
    results.append(("Request Creation", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("Request Creation", False))

# Test 6: Build a prompt (no API call)
print("\n6️⃣ Testing prompt building...")
try:
    from prompts.hackathon_prompt import HackathonPromptBuilder
    
    prompt = HackathonPromptBuilder.build_hackathon_prompt(
        hackathon_name="Test Hackathon",
        project_name="Test Project",
        problem_statement="Test problem",
        solution_description="Test solution",
        tech_stack=["Python", "React"],
        key_features=["Feature 1"],
        team_size=4,
        completion_time_hours=24,
        achievement="participant",
        personal_journey="Test journey",
        key_learnings=["Learning 1"],
        tone="thoughtful",
        audience="developers",
        max_length=3000
    )
    
    assert len(prompt) > 100, "Prompt too short"
    assert "HACKATHON PROJECT DETAILS" in prompt
    assert "Test Hackathon" in prompt
    assert "Test Project" in prompt
    
    print("   ✅ Prompt building working")
    print(f"   📏 Prompt length: {len(prompt)} characters")
    results.append(("Prompt Building", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("Prompt Building", False))

# Test 7: Check app.py integration
print("\n7️⃣ Checking app.py for hackathon integration...")
try:
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()
    
    assert "HACKATHON Project" in app_content, "HACKATHON Project not found in app.py"
    assert "render_hackathon_section" in app_content, "render_hackathon_section not imported in app.py"
    assert "generate_hackathon_post" in app_content, "generate_hackathon_post not called in app.py"
    
    print("   ✅ app.py has hackathon integration")
    results.append(("App Integration", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    results.append(("App Integration", False))

# Summary
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

passed = sum(1 for _, success in results if success)
total = len(results)

for test_name, success in results:
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} - {test_name}")

print("\n" + "=" * 70)
if passed == total:
    print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
    print("=" * 70)
    print("\n✨ Hackathon feature is ready to use!")
    print("\nTo test with Streamlit:")
    print("  streamlit run app.py")
    print("\nSelect '🏆 HACKATHON Project' and fill in the form.")
else:
    print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
    print("=" * 70)

sys.exit(0 if passed == total else 1)
