"""
Hackathon & Competition Post Prompts
====================================
Specialized prompts for generating engaging hackathon project posts.
"""


class HackathonPromptBuilder:
    """Build prompts specifically for hackathon posts"""
    
    @staticmethod
    def build_hackathon_prompt(
        hackathon_name: str,
        project_name: str,
        problem_statement: str,
        solution_description: str,
        tech_stack: list,
        key_features: list,
        team_size: int,
        completion_time_hours: int,
        achievement: str,
        personal_journey: str,
        key_learnings: list,
        tone: str,
        audience: str,
        max_length: int = 3000
    ) -> str:
        """
        Build a hackathon post prompt.
        
        Creates posts with:
        1. Emotional hook (Finally, after years...)
        2. Challenge/problem statement
        3. Solution with technical depth
        4. Team effort and process
        5. Results/achievement
        6. Key learnings
        7. Growth moment
        8. Soft CTA
        """
        
        tech_stack_str = ", ".join(tech_stack) if tech_stack else "multiple technologies"
        features_str = "\n* ".join(key_features) if key_features else ""
        learnings_str = "\n* ".join(key_learnings) if key_learnings else ""
        
        prompt = f"""You are a world-class LinkedIn content creator who specializes in HACKATHON POSTS.

Your posts capture:
✓ The emotional journey ("Finally, after all these years...")
✓ The technical depth and solution
✓ Team collaboration and hustle
✓ Growth and learning
✓ Authentic excitement without hype

HACKATHON PROJECT DETAILS:
├─ Hackathon: {hackathon_name}
├─ Project: {project_name}
├─ Team Size: {team_size} people
├─ Duration: {completion_time_hours} hours
├─ Achievement: {achievement}
└─ Tech Stack: {tech_stack_str}

PROBLEM TO SOLVE:
{problem_statement}

YOUR SOLUTION:
{solution_description}

KEY FEATURES:
{features_str}

YOUR PERSONAL JOURNEY:
{personal_journey}

KEY LEARNINGS:
{learnings_str}

TONE: {tone}
AUDIENCE: {audience}
MAX LENGTH: {max_length} characters

---

HACKATHON POST STRUCTURE (Follow exactly):

SECTION 1 - EMOTIONAL HOOK (2-3 lines):
⚡ The dream-come-true moment
Examples:
- "Finally, after all these years of learning, building, and dreaming… I participated in my first hackathon!"
- "Still processing what just happened."
- "There's something magical about turning an idea into a working prototype in 48 hours."
- "For years, I watched hackathon highlights thinking, 'One day, that will be me.' This weekend, that day finally came."

KEY: Make it PERSONAL, EMOTIONAL, show the journey

SECTION 2 - THE SCENE & EXCITEMENT (1-2 lines):
🎯 Set the stage - where, what, why it matters
Example:
"This weekend at [Hackathon Name], I stepped into an environment I've always admired from afar — fast-paced problem solving, creative chaos, and brilliant minds collaborating under pressure."

SECTION 3 - YOUR PROJECT (2-3 lines):
💡 Introduce the project with excitement
Example:
"Our team built '{project_name}', a {{one-liner description}}.
Using {tech_stack_str}, we designed a system that {{main benefit}}."

SECTION 4 - THE PROBLEM (2-3 lines):
🎭 Make the problem REAL and IMPORTANT
Example:
"{problem_statement}"

Include:
- What's the issue?
- Who does it affect?
- Why is it hard?
- Real-world impact

SECTION 5 - THE SOLUTION (3-5 lines):
💻 TECHNICAL DEEP DIVE
Example:
"We designed a system that:
* {{feature 1}}
* {{feature 2}}
* {{feature 3}}
* {{feature 4}}"

Include specific tech, frameworks, algorithms

SECTION 6 - THE PROCESS (2-3 lines):
🚀 Show what you accomplished in the time limit
Example:
"In just {completion_time_hours} hours, we:
* Built a working prototype
* Integrated live data
* Designed a functional UI
* Delivered a compelling pitch"

SECTION 7 - THE ACHIEVEMENT (1-2 lines):
🏆 Be specific about results
Examples:
- "Our team just secured [Winner] at [Hackathon Name]"
- "We built a complete MVP in {completion_time_hours} hours"
- "Finally, after years of learning, failing, experimenting — I saw one of my ideas presented on stage"

SECTION 8 - KEY LEARNINGS (3-4 bullets):
📚 What this taught you
Example:
"• {{learning 1}}
• {{learning 2}}
• {{learning 3}}"

SECTION 9 - THE REFLECTION (2-3 lines):
🌟 The emotional payoff and growth
Example:
"Walking into that room felt like a dream. Walking out felt like growth.
This hackathon wasn't just an event. It was proof that I'm capable of more than I imagined."

SECTION 10 - SOFT CTA (1-2 lines):
🤝 Question that invites discussion
Examples:
- "What's your biggest blocker when building?"
- "Have you stepped into the arena yet?"
- "If you're building something similar, what's your biggest challenge?"

---

CRITICAL TONE RULES:

IF {tone} == "thoughtful":
- Reflective, meaningful, growth-focused
- "This wasn't just about coding..."
- Focus on learning and personal growth

IF {tone} == "enthusiastic":
- High energy, excitement, "this is amazing"
- "The energy in that room was contagious!"
- Celebrate the wins

IF {tone} == "bold":
- Strong, confident, assertive
- "This proved I'm capable of more"
- Clear opinions and no hesitation

IF {tone} == "casual":
- Conversational, authentic, personal
- "Sleepless? Yes. Worth it? Absolutely."
- Sound like you're talking to a friend

---

AUDIENCE ADJUSTMENTS:

IF {audience} == "developers":
- Technical depth, frameworks, algorithms
- Architecture decisions matter
- Dev struggles and breakthroughs

IF {audience} == "founders":
- Business impact, scalability, team building
- How this could scale to a business
- Market and user insights

IF {audience} == "professionals":
- Career growth, learning outcomes
- Collaboration and teamwork
- Professional development

---

FORBIDDEN PATTERNS (Sound AI-generated):
❌ "We had the opportunity to..."
❌ "Leveraging cutting-edge technologies..."
❌ "We are pleased to announce..."
❌ "Check out our code on GitHub"
❌ Generic "lessons learned"

REQUIRED ELEMENTS:
✓ Specific project name and hackathon name
✓ Specific tech stack (not "web technologies")
✓ Specific problems and solutions
✓ Specific numbers ({completion_time_hours} hours, {team_size} people, etc)
✓ Emotional authenticity
✓ Personal growth moment
✓ Ends with genuine question, not link

---

NOW WRITE THE POST:

Follow the 10-section structure EXACTLY.
Make it emotional AND technical.
Show the journey AND the solution.
Be SPECIFIC about everything.
Sound like someone who just accomplished something meaningful.
Make it feel authentic - not AI-generated.

START WRITING IMMEDIATELY. NO PREAMBLE."""

        return prompt.strip()
