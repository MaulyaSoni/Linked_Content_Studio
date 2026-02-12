"""
Content Formatter - Clean Text Processing
=======================================
Simple formatting utilities for LinkedIn posts.
"""


def format_linkedin_post(text: str, max_length: int = 3000) -> str:
    """
    Format text for LinkedIn posts with optimal readability.
    
    Args:
        text: Raw text content
        max_length: Maximum character limit
        
    Returns:
        Formatted LinkedIn post text
    """
    if not text:
        return ""
    
    # Clean up extra whitespace
    text = " ".join(text.split())
    
    # Ensure proper line breaks for readability
    paragraphs = text.split('\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            # Add line breaks for long paragraphs (mobile-friendly)
            if len(paragraph) > 100:
                # Break at sentence boundaries
                sentences = paragraph.split('. ')
                current_para = ""
                
                for i, sentence in enumerate(sentences):
                    if i < len(sentences) - 1:
                        sentence += "."
                    
                    if len(current_para + sentence) > 100 and current_para:
                        formatted_paragraphs.append(current_para.strip())
                        current_para = sentence + " "
                    else:
                        current_para += sentence + " "
                
                if current_para.strip():
                    formatted_paragraphs.append(current_para.strip())
            else:
                formatted_paragraphs.append(paragraph)
    
    # Join with double line breaks for LinkedIn formatting
    formatted = "\n\n".join(formatted_paragraphs)
    
    # Truncate if too long
    if len(formatted) > max_length:
        formatted = formatted[:max_length-3] + "..."
    
    return formatted


def add_linkedin_formatting(text: str) -> str:
    """
    Add LinkedIn-specific formatting enhancements.
    
    Args:
        text: Plain text content
        
    Returns:
        Text with LinkedIn formatting
    """
    # Add line breaks before bullet points
    text = text.replace("• ", "\n\n• ")
    text = text.replace("- ", "\n\n• ")
    
    # Format common patterns
    text = text.replace("Key takeaways:", "\n\n🔑 Key takeaways:")
    text = text.replace("What I learned:", "\n\n💡 What I learned:")
    text = text.replace("Pro tip:", "\n\n💡 Pro tip:")
    
    # Clean up excessive line breaks
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    
    return text.strip()


def extract_hashtags(text: str) -> str:
    """
    Extract and format hashtags from text.
    
    Args:
        text: Text containing hashtags
        
    Returns:
        Formatted hashtag string
    """
    import re
    
    # Find hashtags in text
    hashtags = re.findall(r'#\w+', text)
    
    if hashtags:
        # Remove duplicates and format
        unique_hashtags = list(dict.fromkeys(hashtags))  # Preserve order
        return " ".join(unique_hashtags)
    
    return ""


def clean_code_snippets(text: str) -> str:
    """
    Format code snippets for LinkedIn readability.
    
    Args:
        text: Text containing code
        
    Returns:
        Text with formatted code snippets
    """
    import re
    
    # Find code blocks and format them
    code_pattern = r'```(\w+)?\n(.*?)```'
    
    def format_code_block(match):
        language = match.group(1) or ""
        code = match.group(2).strip()
        
        # Simple formatting for LinkedIn
        formatted_code = f"\n\n💻 {language.upper() if language else 'CODE'}:\n"
        formatted_code += f"────────────\n{code}\n────────────\n"
        
        return formatted_code
    
    text = re.sub(code_pattern, format_code_block, text, flags=re.DOTALL)
    
    # Format inline code
    text = re.sub(r'`([^`]+)`', r'【\1】', text)
    
    return text