"""
Simple Cache - In-Memory Caching
================================
Lightweight caching for improved performance.
"""

import time
import hashlib
from typing import Any, Optional, Dict, Callable
from functools import wraps


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _generate_key(self, key_func: Callable, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function and arguments."""
        # Create a string representation of the function call
        key_data = {
            'func': key_func.__name__,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        
        # Hash for consistent key length
        key_string = str(key_data)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        
        # Check if expired
        if time.time() > cache_entry['expires_at']:
            self.delete(key)
            return None
        
        # Update access time for LRU
        self._access_times[key] = time.time()
        
        return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest()
        
        # Set cache entry
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + ttl
        }
        
        # Update access time
        self._access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if item was deleted, False if not found
        """
        deleted = key in self._cache
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        return deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
    
    def _evict_oldest(self) -> None:
        """Evict least recently used item."""
        if not self._access_times:
            return
        
        # Find oldest access time
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self.delete(oldest_key)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries.
        
        Returns:
            Number of items removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hit_rate': getattr(self, '_hit_count', 0) / max(1, getattr(self, '_total_requests', 1)),
            'expired_items': self.cleanup_expired()
        }
    
    def memoize(self, ttl: Optional[int] = None):
        """Decorator for memoizing function results.
        
        Args:
            ttl: Time-to-live for cached results
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_key(func, args, kwargs)
                
                # Update stats
                self._total_requests = getattr(self, '_total_requests', 0) + 1
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    self._hit_count = getattr(self, '_hit_count', 0) + 1
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            # Add cache management methods to wrapper
            wrapper.cache_clear = lambda: self.clear()
            wrapper.cache_info = lambda: self.get_stats()
            
            return wrapper
        
        return decorator


# Global cache instance
_global_cache = SimpleCache()


def cache_result(ttl: int = 3600, cache: Optional[SimpleCache] = None):
    """Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        cache: Cache instance (uses global if None)
        
    Returns:
        Decorator function
    """
    cache_instance = cache or _global_cache
    return cache_instance.memoize(ttl)


def get_cache() -> SimpleCache:
    """Get the global cache instance.
    
    Returns:
        Global SimpleCache instance
    """
    return _global_cache


def clear_cache() -> None:
    """Clear the global cache."""
    _global_cache.clear()


def cache_key_from_string(text: str) -> str:
    """Generate cache key from string.
    
    Args:
        text: Input text
        
    Returns:
        Cache key string
    """
    return hashlib.md5(text.encode()).hexdigest()


class LRUCache:
    """Simple LRU (Least Recently Used) cache implementation."""
    
    def __init__(self, capacity: int = 50):
        """Initialize LRU cache.
        
        Args:
            capacity: Maximum number of items
        """
        self.capacity = capacity
        self.cache: Dict[str, Any] = {}
        self.order: list = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value and update order."""
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        self.order.remove(key)
        self.order.append(key)
        
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Put value and update order."""
        if key in self.cache:
            # Update existing
            self.order.remove(key)
            self.order.append(key)
            self.cache[key] = value
        else:
            # Add new
            if len(self.cache) >= self.capacity:
                # Remove least recently used
                oldest = self.order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.order.append(key)
    
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.order.clear()


# Specialized caches for different use cases
class GitHubCache(SimpleCache):
    """Cache for GitHub API responses."""
    
    def __init__(self):
        super().__init__(max_size=50, default_ttl=1800)  # 30 minutes TTL


class LLMCache(SimpleCache):
    """Cache for LLM responses."""
    
    def __init__(self):
        super().__init__(max_size=100, default_ttl=7200)  # 2 hours TTL


class RAGCache(SimpleCache):
    """Cache for RAG context retrieval."""
    
    def __init__(self):
        super().__init__(max_size=30, default_ttl=3600)  # 1 hour TTL


# Cache factory functions
def create_github_cache() -> GitHubCache:
    """Create GitHub cache instance."""
    return GitHubCache()


def create_llm_cache() -> LLMCache:
    """Create LLM cache instance."""
    return LLMCache()


def create_rag_cache() -> RAGCache:
    """Create RAG cache instance."""
    return RAGCache()


if __name__ == "__main__":
    # Test cache functionality
    cache = SimpleCache(max_size=3, default_ttl=1)
    
    # Test basic operations
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key3") is None
    
    # Test memoization
    @cache.memoize(ttl=10)
    def expensive_function(x, y):
        return x * y + time.time()
    
    result1 = expensive_function(2, 3)
    result2 = expensive_function(2, 3)  # Should be cached
    
    assert result1 == result2
    
    # Test LRU
    lru = LRUCache(capacity=2)
    lru.put("a", 1)
    lru.put("b", 2)
    lru.put("c", 3)  # Should evict 'a'
    
    assert lru.get("a") is None
    assert lru.get("b") == 2
    assert lru.get("c") == 3
    
    print("✅ Cache test completed")
