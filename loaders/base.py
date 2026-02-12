"""
Base Loader - Abstract Interface
================================
Abstract base class for all content loaders.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLoader(ABC):
    """Abstract base class for content loaders.
    
    All loaders must inherit from this and implement the load method.
    """
    
    @abstractmethod
    def load(self, source: str) -> Optional[str]:
        """Load content from a source.
        
        Args:
            source: URL, file path, or other source identifier
            
        Returns:
            Loaded content as string, or None if failed
        """
        pass
    
    @abstractmethod
    def is_supported(self, source: str) -> bool:
        """Check if this loader supports the given source.
        
        Args:
            source: URL, file path, or other source identifier
            
        Returns:
            True if this loader can handle the source
        """
        pass
