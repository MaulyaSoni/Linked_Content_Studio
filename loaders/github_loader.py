"""
GitHub Repository Loader for RAG Pipeline.
Supports loading README files and repo metadata from GitHub.
"""

import requests
import re
from typing import List, Optional
from langchain_core.documents import Document


class GitHubLoader:
    """Load content from GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub loader.
        
        Args:
            github_token: Optional GitHub API token for higher rate limits
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"
        self.headers = {}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    def parse_github_url(self, url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL (https://github.com/owner/repo)
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Handle various GitHub URL formats
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$',
            r'^([^/]+)/([^/]+)$'  # owner/repo format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                return owner.strip(), repo.strip()
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def load_readme(self, repo_url: str) -> List[Document]:
        """
        Load README.md from a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            List containing a Document with README content
            
        Raises:
            Exception: If README not found or API request fails
        """
        try:
            owner, repo = self.parse_github_url(repo_url)
            
            # Try common README filenames
            readme_names = ['README.md', 'README.MD', 'README.txt', 'readme.md']
            readme_content = None
            
            for readme_name in readme_names:
                url = f"{self.raw_url}/{owner}/{repo}/main/{readme_name}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    readme_content = response.text
                    break
                
                # Try master branch if main fails
                if readme_name == readme_names[0]:
                    url = f"{self.raw_url}/{owner}/{repo}/master/{readme_name}"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        readme_content = response.text
                        break
            
            if not readme_content:
                raise Exception(f"README not found in repository {owner}/{repo}")
            
            return [Document(
                page_content=readme_content,
                metadata={
                    "source": f"github://{owner}/{repo}",
                    "type": "readme",
                    "repo_url": repo_url
                }
            )]
        
        except Exception as e:
            raise Exception(f"Failed to load README from {repo_url}: {str(e)}")
    
    def load_repo_info(self, repo_url: str) -> List[Document]:
        """
        Load repository metadata from GitHub API.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            List containing a Document with repo metadata
            
        Raises:
            Exception: If API request fails
        """
        try:
            owner, repo = self.parse_github_url(repo_url)
            
            # Get repository info from GitHub API
            api_url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            repo_data = response.json()
            
            # Extract relevant information
            info_text = f"""
Repository: {repo_data.get('full_name', 'N/A')}
URL: {repo_data.get('html_url', 'N/A')}
Description: {repo_data.get('description', 'N/A')}
Stars: {repo_data.get('stargazers_count', 0)}
Language: {repo_data.get('language', 'N/A')}
Topics: {', '.join(repo_data.get('topics', []))}
License: {repo_data.get('license', {}).get('name', 'N/A') if repo_data.get('license') else 'N/A'}
Created: {repo_data.get('created_at', 'N/A')}
Last Updated: {repo_data.get('updated_at', 'N/A')}
Open Issues: {repo_data.get('open_issues_count', 0)}
Forks: {repo_data.get('forks_count', 0)}
"""
            
            return [Document(
                page_content=info_text.strip(),
                metadata={
                    "source": f"github://{owner}/{repo}/info",
                    "type": "repo_info",
                    "repo_url": repo_url,
                    "stars": repo_data.get('stargazers_count', 0),
                    "language": repo_data.get('language', 'Unknown')
                }
            )]
        
        except Exception as e:
            raise Exception(f"Failed to load repo info from {repo_url}: {str(e)}")
    
    def load_files_list(self, repo_url: str) -> List[Document]:
        """
        Load list of files from repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            List containing a Document with file structure
        """
        try:
            owner, repo = self.parse_github_url(repo_url)
            
            api_url = f"{self.base_url}/repos/{owner}/{repo}/contents"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            files_data = response.json()
            
            # Extract file information
            files_text = "Repository Files:\n"
            for item in files_data:
                if isinstance(item, dict):
                    files_text += f"- {item.get('name', 'N/A')} ({item.get('type', 'N/A')})\n"
            
            return [Document(
                page_content=files_text,
                metadata={
                    "source": f"github://{owner}/{repo}/files",
                    "type": "files_list",
                    "repo_url": repo_url
                }
            )]
        
        except Exception as e:
            raise Exception(f"Failed to load files list from {repo_url}: {str(e)}")
    
    def load_repo_complete(self, repo_url: str) -> List[Document]:
        """
        Load complete repository information (README + metadata).
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            List of Documents with README and repository info
        """
        documents = []
        
        # Load README
        try:
            documents.extend(self.load_readme(repo_url))
        except Exception as e:
            print(f"Warning: Could not load README - {str(e)}")
        
        # Load repo metadata
        try:
            documents.extend(self.load_repo_info(repo_url))
        except Exception as e:
            print(f"Warning: Could not load repo info - {str(e)}")
        
        # Load files list
        try:
            documents.extend(self.load_files_list(repo_url))
        except Exception as e:
            print(f"Warning: Could not load files list - {str(e)}")
        
        if not documents:
            raise Exception(f"Failed to load any content from {repo_url}")
        
        return documents
