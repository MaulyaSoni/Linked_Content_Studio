"""
README Fallback Retriever - Production-Ready RAG Degradation
============================================================================
Implements graceful fallback strategy when README is unavailable.

Strategy Hierarchy:
1. README.md (Primary) → If found, use it
2. Repository Metadata → From GitHub API
3. File Structure Analysis → Directory & file tree
4. requirements.txt / package.json → Tech stack
5. Commit Messages → Recent activity & changes
6. Issues & PRs → Problem statements & features
7. Inference Mode → High-level generation with warnings if data insufficient
============================================================================
"""

from typing import List, Dict, Tuple, Optional
from langchain_core.documents import Document
import requests
import json
from datetime import datetime


class ReadmeFallbackRetriever:
    """
    Production-level retriever with graceful degradation when README is missing.
    
    Core Principle:
    "If README is unavailable, shift from documentation-grounded generation
    to repository-intelligence extraction mode"
    """
    
    def __init__(self, repo_url: str, github_token: Optional[str] = None):
        """
        Initialize fallback retriever.
        
        Args:
            repo_url: GitHub repository URL
            github_token: Optional GitHub API token
        """
        self.repo_url = repo_url
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"
        self.headers = self._build_headers()
        
        # Parse repo info
        self.owner, self.repo = self._parse_github_url(repo_url)
        
        # Track what sources are available
        self.available_sources = {
            "readme": False,
            "metadata": False,
            "file_structure": False,
            "requirements": False,
            "commits": False,
            "issues": False
        }
        
        # Store retrieved context
        self.context_data = {}
    
    def _build_headers(self) -> Dict:
        """Build request headers with auth if available."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo."""
        import re
        url = url.rstrip('/')
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$',
            r'^([^/]+)/([^/]+)$'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.groups()
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def retrieve_context(self) -> Tuple[List[Document], Dict]:
        """
        Main orchestration method - implements fallback hierarchy.
        
        Returns:
            (documents, metadata_dict)
            
        Raises:
            Exception: Only if all retrieval methods fail
        """
        documents = []
        
        # Step 1: Try README (Primary)
        print("📄 [Step 1] Trying to load README...")
        readme_docs = self._try_load_readme()
        if readme_docs:
            documents.extend(readme_docs)
            self.available_sources["readme"] = True
            return documents, self._get_retrieval_status()
        
        print("📊 README not available - using repository intelligence sources...")
        
        # Step 2: Load metadata (Fallback Level 1)
        print("🏷️ [Step 2] Loading repository metadata...")
        metadata_docs = self._load_repo_metadata()
        if metadata_docs:
            documents.extend(metadata_docs)
            self.available_sources["metadata"] = True
        
        # Step 3: Load file structure (Fallback Level 2)
        print("📁 [Step 3] Analyzing repository structure...")
        file_structure_docs = self._load_file_structure()
        if file_structure_docs:
            documents.extend(file_structure_docs)
            self.available_sources["file_structure"] = True
        
        # Step 4: Load requirements (Fallback Level 3)
        print("📦 [Step 4] Loading dependencies & tech stack...")
        requirements_docs = self._load_requirements()
        if requirements_docs:
            documents.extend(requirements_docs)
            self.available_sources["requirements"] = True
        
        # Step 5: Load commit messages (Fallback Level 4)
        print("📝 [Step 5] Extracting commit history...")
        commits_docs = self._load_commit_messages()
        if commits_docs:
            documents.extend(commits_docs)
            self.available_sources["commits"] = True
        
        # Step 6: Load issues (Fallback Level 5)
        print("🐛 [Step 6] Loading issues & PRs...")
        issues_docs = self._load_issues()
        if issues_docs:
            documents.extend(issues_docs)
            self.available_sources["issues"] = True
        
        # Validation: Ensure we have some data
        if not documents:
            raise Exception(
                f"❌ README file not found in repository {self.owner}/{self.repo}\n"
                f"   AND no alternative data sources available.\n"
                f"   Cannot generate grounded content.\n"
                f"   Please ensure the repository has at least one of:\n"
                f"   - README.md file\n"
                f"   - Public repository metadata\n"
                f"   - requirements.txt or package.json\n"
                f"   - Commit history\n"
                f"   - Issues or PRs"
            )
        
        return documents, self._get_retrieval_status()
    
    def _try_load_readme(self) -> Optional[List[Document]]:
        """Try to load README.md from repository."""
        try:
            readme_names = ['README.md', 'README.MD', 'README.txt', 'readme.md']
            branches = ['main', 'master', 'develop']
            
            for readme_name in readme_names:
                for branch in branches:
                    url = f"{self.raw_url}/{self.owner}/{self.repo}/{branch}/{readme_name}"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Found README: {readme_name} on branch '{branch}'")
                        return [Document(
                            page_content=response.text,
                            metadata={
                                "source": f"github://{self.owner}/{self.repo}",
                                "type": "readme",
                                "file": readme_name,
                                "branch": branch,
                                "retrieval_level": 1,
                                "retrieval_confidence": "high"
                            }
                        )]
            
            return None
        
        except Exception as e:
            print(f"⚠️  Error trying to load README: {str(e)}")
            return None
    
    def _load_repo_metadata(self) -> Optional[List[Document]]:
        """Load repository metadata from GitHub API."""
        try:
            api_url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            metadata_text = f"""
REPOSITORY METADATA
===================

Repository: {data.get('full_name', 'N/A')}
URL: {data.get('html_url', 'N/A')}
Description: {data.get('description', 'N/A')}

CORE STATS:
-----------
Programming Language: {data.get('language', 'N/A')}
Stars: {data.get('stargazers_count', 0):,}
Forks: {data.get('forks_count', 0):,}
Open Issues: {data.get('open_issues_count', 0)}
Watchers: {data.get('watchers_count', 0)}

TOPICS/TAGS:
{', '.join(data.get('topics', [])) if data.get('topics') else 'N/A'}

LICENSE:
{data.get('license', {}).get('name', 'None') if data.get('license') else 'None'}

TIMELINE:
---------
Created: {data.get('created_at', 'N/A')[:10]}
Last Updated: {data.get('updated_at', 'N/A')[:10]}

VISIBILITY:
-----------
Public: {not data.get('private', False)}
Archived: {data.get('archived', False)}
Disabled: {data.get('disabled', False)}
"""
            
            print("✅ Repository metadata loaded successfully")
            return [Document(
                page_content=metadata_text.strip(),
                metadata={
                    "source": f"github://{self.owner}/{self.repo}",
                    "type": "metadata",
                    "retrieval_level": 2,
                    "retrieval_confidence": "high"
                }
            )]
        
        except Exception as e:
            print(f"⚠️  Failed to load metadata: {str(e)}")
            return None
    
    def _load_file_structure(self) -> Optional[List[Document]]:
        """Analyze and document repository file structure."""
        try:
            api_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            contents = response.json()
            file_structure = self._build_tree_structure(contents, max_depth=3)
            
            structure_text = f"""
REPOSITORY STRUCTURE
====================

Directory Tree:
{file_structure}

KEY FILES IDENTIFIED:
({self._identify_key_files(contents)})

This structure indicates the following about the project:
- Organization: {self._infer_organization(contents)}
- Primary Language: Based on file extensions
- Project Type: {self._infer_project_type(contents)}
"""
            
            print("✅ Repository structure analyzed")
            return [Document(
                page_content=structure_text.strip(),
                metadata={
                    "source": f"github://{self.owner}/{self.repo}",
                    "type": "file_structure",
                    "retrieval_level": 3,
                    "retrieval_confidence": "medium"
                }
            )]
        
        except Exception as e:
            print(f"⚠️  Failed to load file structure: {str(e)}")
            return None
    
    def _build_tree_structure(self, contents: List[Dict], max_depth: int = 3, depth: int = 0, prefix: str = "") -> str:
        """Recursively build file tree structure."""
        if depth > max_depth:
            return ""
        
        tree_str = ""
        for item in sorted(contents, key=lambda x: (x['type'] != 'dir', x['name']))[:20]:  # Limit to 20 items per level
            if item['type'] == 'dir':
                tree_str += f"{prefix}📁 {item['name']}/\n"
            else:
                tree_str += f"{prefix}📄 {item['name']}\n"
        
        return tree_str
    
    def _identify_key_files(self, contents: List[Dict]) -> str:
        """Identify important files in repository."""
        key_files = []
        file_names = [item['name'] for item in contents]
        
        important = ['README.md', 'setup.py', 'package.json', 'requirements.txt', 
                    'Dockerfile', '.github', 'LICENSE', 'CONTRIBUTING.md']
        
        for file_name in important:
            if file_name in file_names:
                key_files.append(f"✓ {file_name}")
        
        return ", ".join(key_files) if key_files else "Standard repository structure"
    
    def _infer_organization(self, contents: List[Dict]) -> str:
        """Infer project organization from structure."""
        structure_patterns = {
            'src': 'Source-first (src/ directory)',
            'lib': 'Library-focused structure',
            'app': 'Application-focused structure',
            'packages': 'Monorepo/multi-package structure',
            'docs': 'Documentation-heavy project',
            'examples': 'Example-driven project'
        }
        
        dirs = [item['name'].lower() for item in contents if item['type'] == 'dir']
        for pattern, desc in structure_patterns.items():
            if pattern in dirs:
                return desc
        
        return "Standard organization"
    
    def _infer_project_type(self, contents: List[Dict]) -> str:
        """Infer project type from files and structure."""
        file_names = [item['name'].lower() for item in contents]
        
        if 'package.json' in file_names or any('node_modules' in f for f in file_names):
            return "JavaScript/Node.js project"
        elif 'setup.py' in file_names or 'requirements.txt' in file_names or 'pyproject.toml' in file_names:
            return "Python project"
        elif 'Gemfile' in file_names:
            return "Ruby project"
        elif any(f.endswith('.sln') or f.endswith('.csproj') for f in file_names):
            return "C#/.NET project"
        else:
            return "Multi-language or utility project"
    
    def _load_requirements(self) -> Optional[List[Document]]:
        """Load tech stack from requirements files (Python/Node)."""
        try:
            requirements_files = ['requirements.txt', 'package.json', 'pyproject.toml', 'Gemfile']
            content = None
            found_file = None
            
            for req_file in requirements_files:
                url = f"{self.raw_url}/{self.owner}/{self.repo}/main/{req_file}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    found_file = req_file
                    break
                
                # Try master branch
                url = f"{self.raw_url}/{self.owner}/{self.repo}/master/{req_file}"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    found_file = req_file
                    break
            
            if not content:
                return None
            
            print(f"✅ Found {found_file}")
            return [Document(
                page_content=content,
                metadata={
                    "source": f"github://{self.owner}/{self.repo}",
                    "type": "requirements",
                    "file": found_file,
                    "retrieval_level": 4,
                    "retrieval_confidence": "high"
                }
            )]
        
        except Exception as e:
            print(f"⚠️  Failed to load requirements: {str(e)}")
            return None
    
    def _load_commit_messages(self, limit: int = 10) -> Optional[List[Document]]:
        """Load and summarize recent commit messages."""
        try:
            api_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits?per_page={limit}"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            commits = response.json()
            
            commits_text = "RECENT COMMIT HISTORY\n" + "="*50 + "\n\n"
            
            for commit in commits[:limit]:
                message = commit['commit']['message'].split('\n')[0]  # First line only
                date = commit['commit']['author']['date'][:10]
                commits_text += f"[{date}] {message}\n"
            
            print(f"✅ Loaded {len(commits)} recent commits")
            return [Document(
                page_content=commits_text.strip(),
                metadata={
                    "source": f"github://{self.owner}/{self.repo}",
                    "type": "commits",
                    "retrieval_level": 5,
                    "retrieval_confidence": "medium"
                }
            )]
        
        except Exception as e:
            print(f"⚠️  Failed to load commits: {str(e)}")
            return None
    
    def _load_issues(self, limit: int = 5) -> Optional[List[Document]]:
        """Load open issues and PRs to understand problems being solved."""
        try:
            api_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues?state=open&per_page={limit}"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            issues = response.json()
            
            if not issues:
                return None
            
            issues_text = "ACTIVE ISSUES & DISCUSSIONS\n" + "="*50 + "\n\n"
            
            for issue in issues[:limit]:
                title = issue['title']
                body_preview = issue['body'][:200] if issue['body'] else "No description"
                body_preview = body_preview.replace('\n', ' ')
                
                issues_text += f"• {title}\n  {body_preview}...\n\n"
            
            print(f"✅ Loaded {len(issues)} open issues")
            return [Document(
                page_content=issues_text.strip(),
                metadata={
                    "source": f"github://{self.owner}/{self.repo}",
                    "type": "issues",
                    "retrieval_level": 6,
                    "retrieval_confidence": "low"
                }
            )]
        
        except Exception as e:
            print(f"⚠️  Failed to load issues: {str(e)}")
            return None
    
    def _get_retrieval_status(self) -> Dict:
        """Return retrieval status and transparency info."""
        active_sources = [k for k, v in self.available_sources.items() if v]
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "repo": f"{self.owner}/{self.repo}",
            "readme_found": self.available_sources["readme"],
            "sources_used": active_sources,
            "source_count": len(active_sources),
            "data_completeness": self._calculate_completeness()
        }
        
        return status
    
    def _calculate_completeness(self) -> str:
        """Calculate data completeness level."""
        active = sum(1 for v in self.available_sources.values() if v)
        total = len(self.available_sources)
        percentage = (active / total) * 100
        
        if percentage >= 80:
            return "high"
        elif percentage >= 50:
            return "medium"
        else:
            return "low"
    
    def get_transparency_message(self) -> str:
        """
        Generate transparency message for UI.
        Shows user what data was used.
        """
        status = self._get_retrieval_status()
        
        if status["readme_found"]:
            return "✅ Post generated from README documentation"
        else:
            sources_str = ", ".join(status["sources_used"])
            completeness = status["data_completeness"]
            
            if completeness == "high":
                return (
                    f"📊 Generated using repository intelligence (README unavailable):\n"
                    f"📊 Sources: {sources_str}\n"
                    f"💡 Data quality: High"
                )
            elif completeness == "medium":
                return (
                    f"📊 README unavailable - using available repository data:\n"
                    f"📊 Sources: {sources_str}\n"
                    f"💡 Recommendation: Add a README for better results"
                )
            else:
                return (
                    f"⚠️ Insufficient data available. Generated with limited context.\n"
                    f"📊 Sources: {sources_str}\n"
                    f"💡 Note: Post may be generic. Consider adding project documentation."
                )
