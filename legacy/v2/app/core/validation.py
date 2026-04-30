"""
Validation Module - Quality Checks
===================================
Validates posts meet quality standards.
"""

import logging
from .models import PostResponse


logger = logging.getLogger(__name__)


def validate_post_response(response: PostResponse) -> PostResponse:
    """Validate and potentially improve post response.
    
    Args:
        response: PostResponse to validate
        
    Returns:
        Validated PostResponse
    """
    if not response.success:
        return response
    
    # Check minimum length
    if len(response.post) < 50:
        logger.warning("Post is too short")
        response.warnings.append("Post may be too short for engagement")
    
    # Check maximum length
    if len(response.post) > response.generation_time > 3000:
        logger.warning("Post exceeds max length")
        response.warnings.append("Post truncated to max length")
    
    # Check for hook
    first_line = response.post.split('\n')[0]
    has_hook = len(first_line) > 5 and len(first_line) < 100
    if not has_hook:
        logger.warning("Weak hook detected")
        response.hook_strength = "weak"
    else:
        response.hook_strength = "strong"
    
    return response
