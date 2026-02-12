"""
Loaders Package - Data Ingestion
================================
Content loaders for various data sources.
"""

from .base import BaseLoader
from .github import GitHubLoader
from .document import DocumentLoader

__all__ = [
    'BaseLoader',
    'GitHubLoader', 
    'DocumentLoader'
]
