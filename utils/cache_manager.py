#!/usr/bin/env python3
"""
Cache Manager for PythonCode Project
Provides Redis-based caching for performance optimization
"""

import redis
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Redis-based cache manager with support for:
    - Key-value caching
    - Function result caching
    - Time-based expiration
    - Cache invalidation
    - Statistics and monitoring
    """
    
    def __init__(self, host='localhost', port=6379, db=0, password=None, 
                 default_ttl=3600, prefix='pythoncode:'):
        """
        Initialize cache manager
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            default_ttl: Default time-to-live in seconds
            prefix: Key prefix for all cache keys
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self.prefix = prefix
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        # Initialize Redis connection
        self._redis = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False,  # We'll handle encoding/decoding
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self._redis.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
        except redis.ConnectionError as e:
            logger.warning(f"Could not connect to Redis: {e}")
            logger.warning("Cache operations will be no-ops")
            self._redis = None
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            self._redis = None
    
    def _is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self._redis is None:
            return False
        
        try:
            self._redis.ping()
            return True
        except:
            return False
    
    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix"""
        return f"{self.prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON serialization first (for simple types)
            if isinstance(value, (dict, list, tuple, str, int, float, bool, type(None))):
                return json.dumps(value).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        if data is None:
            return None
        
        try:
            # Try JSON deserialization first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        if not self._is_connected():
            return default
        
        try:
            full_key = self._make_key(key)
            data = self._redis.get(full_key)
            
            if data is not None:
                self.stats['hits'] += 1
                return self._deserialize(data)
            else:
                self.stats['misses'] += 1
                return default
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            return False
        
        try:
            full_key = self._make_key(key)
            data = self._serialize(value)
            
            if ttl is None:
                ttl = self.default_ttl
            
            if ttl > 0:
                self._redis.setex(full_key, ttl, data)
            else:
                self._redis.set(full_key, data)
            
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            return False
        
        try:
            full_key = self._make_key(key)
            result = self._redis.delete(full_key)
            
            if result > 0:
                self.stats['deletes'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self._is_connected():
            return False
        
        try:
            full_key = self._make_key(key)
            return self._redis.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def ttl(self, key: str) -> Optional[int]:
        """
        Get time-to-live for key
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, or None if key doesn't exist or has no TTL
        """
        if not self._is_connected():
            return None
        
        try:
            full_key = self._make_key(key)
            ttl = self._redis.ttl(full_key)
            
            if ttl == -1:  # No TTL set
                return None
            elif ttl == -2:  # Key doesn't exist
                return None
            else:
                return ttl
                
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for key
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            return False
        
        try:
            full_key = self._make_key(key)
            return self._redis.expire(full_key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    def clear(self, pattern: str = '*') -> int:
        """
        Clear cache keys matching pattern
        
        Args:
            pattern: Redis pattern for keys to delete
            
        Returns:
            Number of keys deleted
        """
        if not self._is_connected():
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = self._redis.keys(full_pattern)
            
            if keys:
                deleted = self._redis.delete(*keys)
                self.stats['deletes'] += deleted
                return deleted
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        stats = self.stats.copy()
        
        if self._is_connected():
            try:
                # Add Redis info
                info = self._redis.info()
                stats.update({
                    'redis_version': info.get('redis_version'),
                    'used_memory_human': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed'),
                    'keyspace_hits': info.get('keyspace_hits'),
                    'keyspace_misses': info.get('keyspace_misses')
                })
            except:
                pass
        
        # Calculate hit rate
        total = stats['hits'] + stats['misses']
        stats['hit_rate'] = stats['hits'] / total if total > 0 else 0
        
        return stats
    
    def reset_stats(self):
        """Reset cache statistics"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def cache_function(self, ttl: Optional[int] = None, key_prefix: str = 'func:'):
        """
        Decorator for caching function results
        
        Args:
            ttl: Time-to-live in seconds
            key_prefix: Prefix for cache keys
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [key_prefix, func.__name__]
                
                # Add args to key
                for arg in args:
                    key_parts.append(str(arg))
                
                # Add kwargs to key
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")
                
                # Create hash of key parts
                key_string = ':'.join(key_parts)
                key_hash = hashlib.md5(key_string.encode()).hexdigest()
                cache_key = f"{key_prefix}{func.__name__}:{key_hash}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Cache miss - execute function
                logger.debug(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Cache the result
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def cache_method(self, ttl: Optional[int] = None, key_prefix: str = 'method:'):
        """
        Decorator for caching method results
        
        Args:
            ttl: Time-to-live in seconds
            key_prefix: Prefix for cache keys
            
        Returns:
            Decorator function
        """
        def decorator(method: Callable):
            @wraps(method)
            def wrapper(self_instance, *args, **kwargs):
                # Generate cache key from instance, method name and arguments
                key_parts = [
                    key_prefix,
                    self_instance.__class__.__name__,
                    method.__name__,
                    str(id(self_instance))  # Include instance ID
                ]
                
                # Add args to key
                for arg in args:
                    key_parts.append(str(arg))
                
                # Add kwargs to key
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")
                
                # Create hash of key parts
                key_string = ':'.join(key_parts)
                key_hash = hashlib.md5(key_string.encode()).hexdigest()
                cache_key = f"{key_prefix}{self_instance.__class__.__name__}:{method.__name__}:{key_hash}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {self_instance.__class__.__name__}.{method.__name__}")
                    return cached_result
                
                # Cache miss - execute method
                logger.debug(f"Cache miss for {self_instance.__class__.__name__}.{method.__name__}")
                result = method(self_instance, *args, **kwargs)
                
                # Cache the result
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator


# Global cache instance
_cache_instance = None

def get_cache_manager() -> CacheManager:
    """
    Get or create global cache manager instance
    
    Returns:
        CacheManager instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = CacheManager()
    
    return _cache_instance

def cache_function(ttl: Optional[int] = None, key_prefix: str = 'func:'):
    """
    Convenience decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorator function
    """
    cache = get_cache_manager()
    return cache.cache_function(ttl, key_prefix)

def cache_method(ttl: Optional[int] = None, key_prefix: str = 'method:'):
    """
    Convenience decorator for caching method results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorator function
    """
    cache = get_cache_manager()
    return cache.cache_method(ttl, key_prefix)


# Example usage
if __name__ == "__main__":
    # Create cache manager
    cache = CacheManager()
    
    # Basic operations
    cache.set("test_key", {"message": "Hello, World!"}, ttl=60)
    value = cache.get("test_key")
    print(f"Retrieved: {value}")
    
    # Function caching example
    @cache_function(ttl=30)
    def expensive_computation(x, y):
        print(f"Computing {x} + {y}...")
        time.sleep(1)  # Simulate expensive computation
        return x + y
    
    # First call - will compute
    result1 = expensive_computation(5, 3)
    print(f"Result 1: {result1}")
    
    # Second call - will use cache
    result2 = expensive_computation(5, 3)
    print(f"Result 2: {result2}")
    
    # Get statistics
    stats = cache.get_stats()
    print(f"\nCache Statistics: {stats}")