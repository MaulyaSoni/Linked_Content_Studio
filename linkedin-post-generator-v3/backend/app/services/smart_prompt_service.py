from typing import Dict, Any, Tuple

class SmartPromptService:
    """Service to inject user context and style into LLM prompts dynamically."""

    async def build_prompt(
        self, topic: str, user_context: Dict[str, Any], tone_override: str | None = None
    ) -> Tuple[str, str]:
        """
        Inject user style into the system and user prompt.
        Returns: (system_prompt, user_prompt)
        """
        tone_to_use = tone_override if tone_override else user_context.get("preferred_tone", "professional")
        recent_topics = ", ".join(user_context.get("recent_topics", []))
        word_count = user_context.get("average_word_count", 150)
        
        # Build core persona and context
        system_prompt = f"""You are an elite LinkedIn content creator and ghostwriter for the user '{user_context.get("first_name", "the client")}'.
Your goal is to write high-engagement, authentic, and valuable LinkedIn posts that sound exactly like the user.

USER PROFILING CONTEXT:
- Tone of Voice: {tone_to_use}
- Typical Content Length: ~{int(word_count)} words
- Frequent Themes: {recent_topics}

RULES FOR LINKEDIN HOOKS:
- Start with a scroll-stopping hook (under 12 words)
- Create an open loop in the first 2 lines
- Do not use clickbait, be authentic

FORMATTING RULES:
- Use sufficient white space (short paragraphs)
- Keep sentences punchy and scannable
- End with an engaging question for the audience
"""

        # Append reference points if available
        past_samples = user_context.get("past_posts_sample", [])
        if past_samples:
            system_prompt += "\n\nHISTORICAL STYLE SAMPLES (Match this style):\n"
            for idx, sample in enumerate(past_samples, 1):
                system_prompt += f"Sample {idx}:\n{sample}\n"

        user_prompt = f"""Please draft a new LinkedIn post on the following topic or idea: "{topic}"

Ensure the post strictly adheres to the tone '{tone_to_use}' and includes relevant emojis naturally.
Include 3-5 highly relevant hashtags at the end.
Provide ONLY the post content, no extra conversational preamble or meta-text.
"""

        return system_prompt, user_prompt
