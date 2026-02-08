
HASHTAG_PROMPT = """
Generate relevant LinkedIn hashtags based on the post content.

Rules:
- Maximum 10 hashtags
- Prioritize relevance over quantity
- Include:
  - 4 tech hashtags (specific technologies mentioned)
  - 2 role hashtags (job functions or roles)
  - 2-3 trend/community hashtags (industry trends or communities)
- Avoid repeating similar hashtags
- Avoid generic tags like #Tech unless truly relevant
- Format: #Hashtag1 #Hashtag2 #Hashtag3 etc.

Post Content:
{content}

Hashtags:
"""
