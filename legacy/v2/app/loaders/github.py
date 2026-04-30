"""
GitHub Loader - Repository Content Extraction
============================================
Loads and processes GitHub repository content for RAG.
"""

import os
import re
import logging
from typing import Optional, List, Dict, Any
from .base import BaseLoader


logger = logging.getLogger(__name__)


class GitHubLoader(BaseLoader):
    """GitHub repository loader with fallback strategies."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub loader.
        
        Args:
            token: GitHub personal access token (optional but recommended)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.github_client = None
        
        # Initialize GitHub client if token available
        if self.token:
            try:
                from github import Github
                self.github_client = Github(self.token)
                logger.info("✅ GitHub client initialized with token")
            except ImportError:
                logger.warning("PyGithub not installed, using fallback methods")
        else:
            logger.info("⚠️ No GitHub token, using public API only")
    
    def load(self, github_url: str) -> Optional[str]:
        """Load content from GitHub repository.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Repository content as string, or None if failed
        """
        try:
            # Parse GitHub URL
            owner, repo = self._parse_github_url(github_url)
            if not owner or not repo:
                logger.error(f"Invalid GitHub URL: {github_url}")
                return None
            
            logger.info(f"📥 Loading GitHub repo: {owner}/{repo}")
            
            # Try with GitHub client first (if available)
            if self.github_client:
                content = self._load_with_client(owner, repo)
                if content:
                    return content
            
            # Fallback to public API
            content = self._load_with_public_api(owner, repo)
            if content:
                return content
            
            # Final fallback: basic info
            return self._load_basic_info(owner, repo)
            
        except Exception as e:
            logger.error(f"❌ GitHub loading failed: {e}")
            return None
    
    def is_supported(self, source: str) -> bool:
        """Check if source is a valid GitHub URL."""
        return self._is_valid_github_url(source)
    
    def _parse_github_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Parse GitHub URL to extract owner and repo."""
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'^([^/]+)/([^/]+)/?$'  # username/repo format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)
        
        return None, None
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub URL format."""
        owner, repo = self._parse_github_url(url)
        return owner is not None and repo is not None
    
    def _load_with_client(self, owner: str, repo: str) -> Optional[str]:
        """Load using GitHub client (authenticated)."""
        try:
            repository = self.github_client.get_repo(f"{owner}/{repo}")
            
            # Get README
            readme_content = ""
            try:
                readme = repository.get_readme()
                readme_content = readme.decoded_content.decode('utf-8')
                logger.info("✅ README loaded via GitHub client")
            except Exception as e:
                logger.warning(f"README not found: {e}")
            
            # Get repository info
            repo_info = self._get_repo_info(repository)
            
            # Get file structure (top level)
            file_structure = self._get_file_structure(repository)
            
            # Get recent commits
            recent_commits = self._get_recent_commits(repository)
            
            # Combine all content
            content_parts = []
            
            if repo_info:
                content_parts.append(f"REPOSITORY INFO:\n{repo_info}")
            
            if readme_content:
                content_parts.append(f"README:\n{readme_content[:2000]}")
            
            if file_structure:
                content_parts.append(f"FILE STRUCTURE:\n{file_structure}")
            
            if recent_commits:
                content_parts.append(f"RECENT COMMITS:\n{recent_commits}")
            
            return "\n\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"GitHub client loading failed: {e}")
            return None
    
    def _load_with_public_api(self, owner: str, repo: str) -> Optional[str]:
        """Load using public GitHub API (no authentication)."""
        try:
            import requests
            
            # Get repository info
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(repo_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"GitHub API error: {response.status_code}")
                return None
            
            repo_data = response.json()
            
            # Get README
            readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            readme_response = requests.get(readme_url, timeout=10)
            
            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get('content'):
                    import base64
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # Build content
            content_parts = []
            
            # Repository information
            repo_info = f"""Name: {repo_data.get('name', 'N/A')}
Description: {repo_data.get('description', 'N/A')}
Language: {repo_data.get('language', 'N/A')}
Stars: {repo_data.get('stargazers_count', 0)}
Topics: {', '.join(repo_data.get('topics', []))}
Created: {repo_data.get('created_at', 'N/A')}
Updated: {repo_data.get('updated_at', 'N/A')}"""
            
            content_parts.append(f"REPOSITORY INFO:\n{repo_info}")
            
            if readme_content:
                content_parts.append(f"README:\n{readme_content[:2000]}")
            
            return "\n\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"Public API loading failed: {e}")
            return None
    
    def _load_basic_info(self, owner: str, repo: str) -> str:
        """Fallback: return basic repository information."""
        return f"""GitHub Repository: {owner}/{repo}

This is a GitHub repository. Additional details could not be retrieved.
This may be due to:
- Repository being private
- Rate limiting on GitHub API
- Network connectivity issues

For better results, consider:
1. Setting GITHUB_TOKEN environment variable
2. Ensuring repository is public
3. Checking network connection"""
    
    def _get_repo_info(self, repository) -> str:
        """Extract repository information."""
        try:
            return f"""Name: {repository.name}
Description: {repository.description or 'N/A'}
Language: {repository.language or 'N/A'}
Stars: {repository.stargazers_count}
Forks: {repository.forks_count}
Topics: {', '.join(repository.get_topics())}
Created: {repository.created_at}
Updated: {repository.updated_at}
Default Branch: {repository.default_branch}"""
        except Exception as e:
            logger.warning(f"Failed to get repo info: {e}")
            return ""
    
    def _get_file_structure(self, repository, max_files: int = 20) -> str:
        """Get top-level file structure."""
        try:
            files = []
            try:
                contents = repository.get_contents("")
                for content in contents[:max_files]:
                    if content.type == "dir":
                        files.append(f"📁 {content.name}/")
                    else:
                        files.append(f"📄 {content.name}")
            except Exception as e:
                logger.warning(f"Failed to get file structure: {e}")
                return ""
            
            return "\n".join(files)
        except Exception as e:
            logger.warning(f"File structure extraction failed: {e}")
            return ""
    
    def _get_recent_commits(self, repository, max_commits: int = 5) -> str:
        """Get recent commit messages."""
        try:
            commits = []
            try:
                for commit in repository.get_commits()[:max_commits]:
                    message = commit.commit.message.split('\n')[0]  # First line only
                    commits.append(f"• {message}")
            except Exception as e:
                logger.warning(f"Failed to get commits: {e}")
                return ""
            
            return "\n".join(commits)
        except Exception as e:
            logger.warning(f"Commit extraction failed: {e}")
            return ""
