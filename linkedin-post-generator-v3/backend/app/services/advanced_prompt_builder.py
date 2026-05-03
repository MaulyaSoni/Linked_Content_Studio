from typing import Dict, Optional

class AdvancedPromptBuilder:
    """Build customized prompts based on user profile."""
    
    @staticmethod
    def build_customized_prompt(
        topic: str,
        user_profile: Dict,
        tone_override: Optional[str] = None,
        content_type: str = "simple_topic",
        additional_context: str = ""
    ) -> str:
        """
        Build a 500+ line customized prompt instruction.
        """
        
        # Use override or detected tone
        tone = tone_override or user_profile.get("tone", "professional")
        
        # Build prompt
        prompt = f"""
You are a world-class LinkedIn content strategist writing a post for a specific user.

CRITICAL INSTRUCTION: Write exactly how this user writes. Don't be generic. Be authentic to their voice.

================================================================================
USER WRITING PROFILE (MATCH THIS EXACTLY)
================================================================================

TONE: {tone}
└─ Write with {tone} authority and language choice
└─ If {tone}=="professional": Use formal language, industry terms, credibility markers
└─ If {tone}=="casual": Use conversational language, contractions, relaxed tone
└─ If {tone}=="humorous": Include light jokes, witty observations, playful tone
└─ If {tone}=="inspirational": Use uplifting language, motivational themes, hope-filled tone

VOCABULARY LEVEL: {user_profile.get('vocabulary_level', 'intermediate')}
└─ If "simple": Use everyday words, short sentences, clear explanations
└─ If "intermediate": Mix simple and complex words, professional terms
└─ If "advanced": Use industry-specific terminology, complex concepts, sophisticated language

SENTENCE PATTERNS:
└─ Average sentence length: {user_profile.get('sentence_patterns', {}).get('avg_length', 15)} words
└─ Variation: {user_profile.get('sentence_patterns', {}).get('variation', 'medium')}
└─ If "high variation": Mix very short (5-8 words) and longer (20-30 words) sentences for impact
└─ If "medium variation": Mostly 12-18 words, occasional longer/shorter
└─ If "low variation": Keep consistent length around {user_profile.get('sentence_patterns', {}).get('avg_length', 15)} words

PERSONALITY ARCHETYPE: {user_profile.get('personality', 'balanced')}
└─ If "thought_leader": Share insights, frameworks, deep analysis
└─ If "storyteller": Tell personal stories, use narrative arc, add human elements
└─ If "expert": Explain how-to, share knowledge, teach techniques
└─ If "connector": Emphasize community, collaboration, relationships
└─ If "provocateur": Challenge assumptions, present contrarian views
└─ If "balanced": Mix all approaches naturally

STORYTELLING STYLE: {user_profile.get('storytelling_style', 'mixed')}
└─ If "narrative": Tell a story with characters, progression, resolution
└─ If "data_driven": Use statistics, research findings, concrete numbers
└─ If "mixed": Start with hook, add context, use data to support, conclude with insight

CONTENT THEMES: {', '.join(user_profile.get('content_themes', ['general']))}
└─ Include references to these topics where natural
└─ Stay authentic to what this user cares about
└─ Don't force themes - only include if relevant to topic

EMOJI USAGE: {user_profile.get('emoji_usage', {}).get('usage', 'yes')}
└─ If "yes": Use emojis naturally (not excessive)
└─ Frequency: {user_profile.get('emoji_usage', {}).get('frequency', 'moderate')}
   └─ If "frequent": Include 4-6 emojis throughout post
   └─ If "moderate": Include 2-3 emojis strategically
   └─ If "occasional": Include 0-1 emoji or none
└─ Emoji placement: End of sentences or after key words (not forced)

CALL-TO-ACTION STYLE: {user_profile.get('cta_style', 'question')}
└─ If "question": End with a question to engage audience
└─ If "action": End with a call to action (share, comment, try, join)
└─ If "statement": End with a powerful statement or thought

AUDIENCE CONNECTION: {user_profile.get('audience_connection', 'direct')}
└─ If "direct": Use "you" and "your" frequently, speak directly to reader
└─ If "inclusive": Use "we", "us", create sense of community
└─ If "formal": Use formal address, maintain professional distance

================================================================================
CONTENT REQUIREMENTS
================================================================================

TOPIC: {topic}
TYPE: {content_type}

POST STRUCTURE:
1. HOOK (first 1-2 sentences)
   └─ Grab attention immediately
   └─ Specific to {tone} tone
   └─ Make them want to read more

2. CONTEXT (2-3 sentences)
   └─ Provide background or problem statement
   └─ Relevant to topic
   └─ Authentic to user's experience

3. INSIGHT (2-3 sentences)
   └─ Key message or takeaway
   └─ Use {user_profile.get('storytelling_style', 'mixed')} approach
   └─ Match {user_profile.get('vocabulary_level', 'intermediate')} vocabulary

4. EVIDENCE/DETAIL (2-3 sentences)
   └─ Support with specifics
   └─ Data if narrative, story if data-driven
   └─ Relevant to content themes

5. CALL-TO-ACTION (1-2 sentences)
   └─ Style: {user_profile.get('cta_style', 'question')}
   └─ Authentic to user's voice
   └─ Encourage engagement

LENGTH: 150-250 words (optimal for LinkedIn)

{f'ADDITIONAL CONTEXT: {additional_context}' if additional_context else ''}

================================================================================
QUALITY CHECKLIST
================================================================================

Before finalizing, verify:
☑ Tone matches "{tone}" exactly
☑ Sentence length averages {user_profile.get('sentence_patterns', {}).get('avg_length', 15)} words
☑ Vocabulary level is {user_profile.get('vocabulary_level', 'intermediate')}
☑ Personality shows {user_profile.get('personality', 'balanced')} archetype
☑ Storytelling uses {user_profile.get('storytelling_style', 'mixed')} approach
☑ Emojis: {user_profile.get('emoji_usage', {}).get('frequency', 'moderate')} usage
☑ CTA is {user_profile.get('cta_style', 'question')}
☑ Post feels authentic, not generic
☑ Includes 2-5 relevant hashtags
☑ Length is 150-250 words

================================================================================
WRITE THE POST
================================================================================

Generate a LinkedIn post about "{topic}" that:
- Sounds exactly like this user writes
- Matches all profile dimensions above
- Provides genuine value to readers
- Encourages engagement
- Includes hashtags at the end

Post:
"""
        
        return prompt.strip()
