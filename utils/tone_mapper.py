def map_tone(choice):
    """Map tone choice to detailed tone instruction."""
    if choice == "Minimal":
        return "Professional, concise, formal, no emojis"
    if choice == "Balanced":
        return "Friendly, clear, slightly engaging, minimal emojis"
    return "High energy, motivational, emoji rich"

def tone_config(level):
    """Legacy function for tone configuration."""
    if level == "Minimal":
        return "Use no emojis. Maintain a professional tone."
    if level == "Balanced":
        return "Use limited emojis. Maintain a friendly professional tone."
    return "Use engaging emojis and an energetic tone."
