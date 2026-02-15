"""
tests/test_hackathon.py
Test hackathon post generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import LinkedInGenerator
from core.models import (
    HackathonProjectRequest,
    HackathonType,
    HackathonAchievement,
    Tone
)


def test_hackathon_basic():
    """Test basic hackathon post generation"""
    
    print("\n🏆 Testing Hackathon Post Generation...")
    
    try:
        gen = LinkedInGenerator()
        
        # Create test request
        request = HackathonProjectRequest(
            hackathon_name="Odoo X Adani Hackathon",
            project_name="WaterFlow - Smart City Water Management",
            hackathon_type=HackathonType.SUSTAINABILITY,
            team_size=5,
            team_members=["Alice", "Bob", "Charlie", "Diana", "Eve"],
            problem_statement="City water management affects millions worldwide. Aging infrastructure, inefficient supply chains, and lack of real-time monitoring make it difficult for municipalities to ensure clean water reaches every household.",
            solution_description="We built an ML model integrated with MERN stack that detects anomalies in water usage patterns. By integrating an ML model with our application, we were able to identify potential issues before they became major problems, enabling proactive maintenance and reducing waste.",
            tech_stack=["React", "Node.js", "MongoDB", "Python", "ML", "Google Maps API"],
            key_features=[
                "Real-time anomaly detection in water usage",
                "Pattern recognition using clustering and regression",
                "Proactive maintenance alerts",
                "Interactive monitoring dashboard"
            ],
            completion_time_hours=24,
            achievement=HackathonAchievement.WINNER,
            personal_journey="Finally, after 6 years of learning, building, and dreaming… I stood on stage presenting a solution that could help millions.",
            key_learnings=[
                "Real-time data processing requires careful optimization",
                "Machine learning can solve real-world problems",
                "Team collaboration under constraints sparks innovation",
                "Technical depth matters but communication matters more"
            ]
        )
        
        # Validate request
        request.validate()
        print("✅ Request validation passed")
        
        # Generate post
        print("🚀 Generating post...")
        response = gen.generate_hackathon_post(request)
        
        # Check response
        assert response.success, f"Generation failed: {response.error_message}"
        assert len(response.post) > 500, "Post too short"
        assert response.achievement_level == "winner", "Achievement not set correctly"
        assert response.generation_time > 0, "Generation time not recorded"
        
        print(f"✅ Post generated in {response.generation_time:.2f}s")
        print(f"✅ Post length: {len(response.post)} characters")
        print(f"✅ Achievement: {response.achievement_level}")
        print(f"\n📱 Generated Post:\n{response.post}")
        print(f"\n#️⃣ Hashtags:\n{response.hashtags}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hackathon_participant():
    """Test participant-level hackathon post"""
    
    print("\n🏆 Testing Participant-Level Post...")
    
    try:
        gen = LinkedInGenerator()
        
        request = HackathonProjectRequest(
            hackathon_name="HackUVA 2024",
            project_name="GreenRoute",
            team_size=4,
            problem_statement="Delivery drivers waste fuel on inefficient routes, increasing carbon emissions and costs.",
            solution_description="Smart route optimization using Python, Google Maps API, and ML algorithms to suggest eco-efficient routes in real time.",
            tech_stack=["Python", "Google Maps API", "React", "Node.js"],
            key_features=[
                "Real-time traffic analysis",
                "ML-based route optimization",
                "Carbon emission tracking",
                "Driver mobile interface"
            ],
            completion_time_hours=24,
            achievement=HackathonAchievement.PARTICIPANT,
            personal_journey="For years, I watched hackathon highlights thinking 'One day, that will be me.' This weekend, that day finally came.",
            key_learnings=[
                "Time constraints breed innovation",
                "Diverse teams ship faster",
                "I'm capable of building real solutions"
            ]
        )
        
        response = gen.generate_hackathon_post(request)
        
        assert response.success
        assert response.achievement_level == "participant"
        assert len(response.post) > 400
        
        print("✅ Participant post test passed!")
        print(f"✅ Estimated reach: {response.estimated_reach}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    results = []
    
    print("=" * 60)
    print("HACKATHON POST GENERATION TESTS")
    print("=" * 60)
    
    results.append(("Basic Generation (Winner)", test_hackathon_basic()))
    results.append(("Participant Level", test_hackathon_participant()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
