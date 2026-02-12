"""
Custom Exceptions for Production RAG System
============================================================================
Provides clear, actionable exceptions without hallucination.
"""


class ReadmeNotFoundException(Exception):
    """
    Raised when README is not found in repository.
    Prevents system from attempting to generate hallucinated content.
    """
    def __init__(self, repo_name: str, available_sources: list = None):
        self.repo_name = repo_name
        self.available_sources = available_sources or []
        
        message = (
            f"\n❌ README FILE NOT FOUND IN REPOSITORY: {repo_name}\n"
            f"{'='*70}\n"
            f"\n📄 The README.md file could not be accessed from this repository.\n"
            f"\n   This is a hard stop—we will NOT generate hallucinated content.\n"
            f"\n✅ SOLUTION OPTIONS:\n"
            f"   1. Ensure README.md exists in the main or master branch\n"
            f"   2. Make sure the repository is public (or provide a GitHub token)\n"
            f"   3. Check that the file is named 'README.md' (case-sensitive on some systems)\n"
            f"\n📊 ALTERNATIVE: Repository Intelligence Mode\n"
            f"   System can generate posts from repository metadata, file structure,\n"
            f"   and commit history IF these are available.\n"
            f"\n⚠️  Current Status: Insufficient accessible data to proceed safely.\n"
            f"{'='*70}\n"
        )
        
        super().__init__(message)


class InsufficientRepositoryDataException(Exception):
    """
    Raised when repository has no accessible content sources.
    """
    def __init__(self, repo_name: str):
        message = (
            f"\n❌ INSUFFICIENT DATA - CANNOT PROCEED SAFELY\n"
            f"{'='*70}\n"
            f"\nRepository: {repo_name}\n"
            f"\n❌ No accessible data sources found.\n"
            f"   We cannot generate a grounded, hallucination-free post.\n"
            f"\n📋 The repository needs at least one of:\n"
            f"   • README.md file\n"
            f"   • Package file (requirements.txt, package.json, etc.)\n"
            f"   • Commit history (public repository)\n"
            f"   • GitHub issues/discussions\n"
            f"\n✅ What to do:\n"
            f"   1. Make repository public\n"
            f"   2. Add a README.md file\n"
            f"   3. Ensure you have API access (provide GitHub token if private)\n"
            f"{'='*70}\n"
        )
        super().__init__(message)


class RepositoryAccessException(Exception):
    """
    Raised when repository cannot be accessed due to permissions/network issues.
    """
    def __init__(self, repo_name: str, reason: str):
        message = (
            f"\n❌ REPOSITORY ACCESS FAILED\n"
            f"{'='*70}\n"
            f"\nRepository: {repo_name}\n"
            f"Reason: {reason}\n"
            f"\n⚠️  We cannot verify repository content safety.\n"
            f"\n✅ Troubleshooting:\n"
            f"   • Check internet connection\n"
            f"   • Verify repository URL is correct\n"
            f"   • For private repos, provide a GitHub token\n"
            f"   • Check GitHub API rate limits\n"
            f"{'='*70}\n"
        )
        super().__init__(message)


class DataQualityWarning(Exception):
    """
    Raised when data quality is low but generation can proceed.
    Shows user that post may be generic.
    """
    def __init__(self, completeness_level: str, sources: list):
        sources_str = ", ".join(sources)
        message = (
            f"\n⚠️  LOW DATA QUALITY WARNING\n"
            f"{'='*70}\n"
            f"\n📊 Data Completeness: {completeness_level}\n"
            f"📋 Sources Available: {sources_str}\n"
            f"\n⚠️  The generated post may be generic or lack specificity.\n"
            f"\n💡 Recommendation:\n"
            f"   Add a comprehensive README.md to improve post quality.\n"
            f"{'='*70}\n"
        )
        super().__init__(message)
