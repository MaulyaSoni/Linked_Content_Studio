"""
Custom Exceptions - Clean Error Handling
========================================
Custom exception classes for better error management.
"""

from typing import Optional, Dict, Any


class LinkedInGeneratorError(Exception):
    """Base exception for LinkedIn post generator."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """Initialize base exception.
        
        Args:
            message: Error message
            error_code: Optional error code
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context
        }


class ConfigurationError(LinkedInGeneratorError):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, missing_config: Optional[str] = None):
        """Initialize configuration error.
        
        Args:
            message: Error message
            missing_config: Name of missing configuration
        """
        context = {"missing_config": missing_config} if missing_config else {}
        super().__init__(message, error_code="CONFIG_ERROR", context=context)


class LLMError(LinkedInGeneratorError):
    """Raised when LLM operations fail."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM error.
        
        Args:
            message: Error message
            provider: LLM provider name
            model: Model name
        """
        context = {}
        if provider:
            context["provider"] = provider
        if model:
            context["model"] = model
        
        super().__init__(message, error_code="LLM_ERROR", context=context)


class RAGError(LinkedInGeneratorError):
    """Raised when RAG operations fail."""
    
    def __init__(self, message: str, source_type: Optional[str] = None, source: Optional[str] = None):
        """Initialize RAG error.
        
        Args:
            message: Error message
            source_type: Type of source (github, document, etc.)
            source: Source identifier
        """
        context = {}
        if source_type:
            context["source_type"] = source_type
        if source:
            context["source"] = source
        
        super().__init__(message, error_code="RAG_ERROR", context=context)


class ValidationError(LinkedInGeneratorError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field name that failed validation
            value: Value that failed validation
        """
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        
        super().__init__(message, error_code="VALIDATION_ERROR", context=context)


class GitHubError(LinkedInGeneratorError):
    """Raised when GitHub operations fail."""
    
    def __init__(self, message: str, repo_url: Optional[str] = None, api_error: Optional[str] = None):
        """Initialize GitHub error.
        
        Args:
            message: Error message
            repo_url: Repository URL
            api_error: API error message
        """
        context = {}
        if repo_url:
            context["repo_url"] = repo_url
        if api_error:
            context["api_error"] = api_error
        
        super().__init__(message, error_code="GITHUB_ERROR", context=context)


class DocumentError(LinkedInGeneratorError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, file_type: Optional[str] = None):
        """Initialize document error.
        
        Args:
            message: Error message
            file_path: File path
            file_type: File type/extension
        """
        context = {}
        if file_path:
            context["file_path"] = file_path
        if file_type:
            context["file_type"] = file_type
        
        super().__init__(message, error_code="DOCUMENT_ERROR", context=context)


class GenerationError(LinkedInGeneratorError):
    """Raised when post generation fails."""
    
    def __init__(self, message: str, mode: Optional[str] = None, content_type: Optional[str] = None):
        """Initialize generation error.
        
        Args:
            message: Error message
            mode: Generation mode (simple/advanced)
            content_type: Content type being generated
        """
        context = {}
        if mode:
            context["mode"] = mode
        if content_type:
            context["content_type"] = content_type
        
        super().__init__(message, error_code="GENERATION_ERROR", context=context)


class APIError(LinkedInGeneratorError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, service: Optional[str] = None, status_code: Optional[int] = None):
        """Initialize API error.
        
        Args:
            message: Error message
            service: Service name (GitHub, Groq, etc.)
            status_code: HTTP status code
        """
        context = {}
        if service:
            context["service"] = service
        if status_code:
            context["status_code"] = status_code
        
        super().__init__(message, error_code="API_ERROR", context=context)


class TimeoutError(LinkedInGeneratorError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout_seconds: Optional[float] = None):
        """Initialize timeout error.
        
        Args:
            message: Error message
            operation: Operation that timed out
            timeout_seconds: Timeout duration
        """
        context = {}
        if operation:
            context["operation"] = operation
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        
        super().__init__(message, error_code="TIMEOUT_ERROR", context=context)


# Error handling utilities
def handle_exception(func):
    """Decorator for consistent exception handling."""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LinkedInGeneratorError:
            # Re-raise custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise LinkedInGeneratorError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                context={"function": func.__name__, "original_error": str(e)}
            ) from e
    
    return wrapper


def format_error_for_user(error: Exception) -> str:
    """Format exception for user-friendly display.
    
    Args:
        error: Exception instance
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, ConfigurationError):
        return "⚙️ Configuration issue: Please check your API keys and settings."
    elif isinstance(error, LLMError):
        return "🤖 AI service unavailable: Please try again in a moment."
    elif isinstance(error, RAGError):
        return "📚 Content analysis failed: Using simple mode instead."
    elif isinstance(error, ValidationError):
        return "❌ Invalid input: Please check your input and try again."
    elif isinstance(error, GitHubError):
        return "📂 GitHub access issue: Please check the repository URL."
    elif isinstance(error, DocumentError):
        return "📄 File processing error: Please check your file format."
    elif isinstance(error, GenerationError):
        return "✍️ Generation failed: Please try a different topic or input."
    elif isinstance(error, APIError):
        return "🌐 Service unavailable: Please check your internet connection."
    elif isinstance(error, TimeoutError):
        return "⏰ Request timed out: Please try again."
    else:
        return "❌ Something went wrong: Please try again."


def log_exception(logger, error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log exception with structured information.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
    """
    if isinstance(error, LinkedInGeneratorError):
        logger.error(
            error.message,
            error_type=error.__class__.__name__,
            error_code=error.error_code,
            **{**error.context, **(context or {})}
        )
    else:
        logger.error(
            str(error),
            error_type=error.__class__.__name__,
            **(context or {})
        )


# Exception factory functions
def create_config_error(missing_key: str) -> ConfigurationError:
    """Create configuration error for missing key."""
    return ConfigurationError(
        f"Missing required configuration: {missing_key}",
        missing_config=missing_key
    )


def create_llm_error(message: str, provider: str = "unknown") -> LLMError:
    """Create LLM error."""
    return LLMError(message, provider=provider)


def create_validation_error(field: str, value: Any, reason: str) -> ValidationError:
    """Create validation error."""
    return ValidationError(
        f"Invalid {field}: {reason}",
        field=field,
        value=value
    )


def create_github_error(repo_url: str, api_message: str) -> GitHubError:
    """Create GitHub error."""
    return GitHubError(
        f"Failed to access GitHub repository: {api_message}",
        repo_url=repo_url,
        api_error=api_message
    )


if __name__ == "__main__":
    # Test exceptions
    try:
        raise ConfigurationError("Missing API key", missing_config="GROQ_API_KEY")
    except ConfigurationError as e:
        print(f"Caught exception: {e.to_dict()}")
    
    try:
        raise ValidationError("Invalid GitHub URL", field="github_url", value="invalid-url")
    except ValidationError as e:
        print(f"Caught validation error: {e.to_dict()}")
    
    print("✅ Exception handling test completed")
