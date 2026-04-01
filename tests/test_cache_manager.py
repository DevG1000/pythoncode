#!/usr/bin/env python3
"""
Tests for Cache Manager
"""

import unittest
import time
from unittest.mock import Mock, patch
from utils.cache_manager import CacheManager, cache_function, cache_method

class TestCacheManager(unittest.TestCase):
    """Test CacheManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock Redis connection
        self.cache = CacheManager()
        self.cache._redis = Mock()
        self.cache._is_connected = Mock(return_value=True)
    
    def test_make_key(self):
        """Test key creation with prefix"""
        key = self.cache._make_key("test_key")
        self.assertEqual(key, "pythoncode:test_key")
    
    def test_serialize_deserialize_json(self):
        """Test JSON serialization/deserialization"""
        test_data = {"name": "test", "value": 123, "list": [1, 2, 3]}
        
        serialized = self.cache._serialize(test_data)
        deserialized = self.cache._deserialize(serialized)
        
        self.assertEqual(deserialized, test_data)
    
    def test_serialize_deserialize_pickle(self):
        """Test pickle serialization/deserialization"""
        # Create a complex object
        class TestObject:
            def __init__(self, value):
                self.value = value
            
            def __eq__(self, other):
                return self.value == other.value
        
        test_obj = TestObject(42)
        
        serialized = self.cache._serialize(test_obj)
        deserialized = self.cache._deserialize(serialized)
        
        self.assertEqual(deserialized.value, test_obj.value)
    
    def test_get_set(self):
        """Test get and set operations"""
        test_key = "test_key"
        test_value = {"data": "test"}
        
        # Mock Redis get/set
        self.cache._redis.get.return_value = self.cache._serialize(test_value)
        self.cache._redis.setex.return_value = True
        
        # Test set
        result = self.cache.set(test_key, test_value, ttl=60)
        self.assertTrue(result)
        
        # Test get
        retrieved = self.cache.get(test_key)
        self.assertEqual(retrieved, test_value)
        
        # Verify Redis was called
        self.cache._redis.setex.assert_called_once()
        self.cache._redis.get.assert_called_once()
    
    def test_get_with_default(self):
        """Test get with default value"""
        test_key = "non_existent_key"
        default_value = "default"
        
        # Mock Redis to return None (key doesn't exist)
        self.cache._redis.get.return_value = None
        
        retrieved = self.cache.get(test_key, default_value)
        self.assertEqual(retrieved, default_value)
    
    def test_delete(self):
        """Test delete operation"""
        test_key = "test_key"
        
        # Mock Redis delete
        self.cache._redis.delete.return_value = 1
        
        result = self.cache.delete(test_key)
        self.assertTrue(result)
        self.cache._redis.delete.assert_called_once()
    
    def test_exists(self):
        """Test exists operation"""
        test_key = "test_key"
        
        # Mock Redis exists
        self.cache._redis.exists.return_value = 1
        
        result = self.cache.exists(test_key)
        self.assertTrue(result)
        self.cache._redis.exists.assert_called_once()
    
    def test_ttl(self):
        """Test TTL operation"""
        test_key = "test_key"
        
        # Mock Redis TTL
        self.cache._redis.ttl.return_value = 30
        
        ttl = self.cache.ttl(test_key)
        self.assertEqual(ttl, 30)
        self.cache._redis.ttl.assert_called_once()
    
    def test_expire(self):
        """Test expire operation"""
        test_key = "test_key"
        
        # Mock Redis expire
        self.cache._redis.expire.return_value = True
        
        result = self.cache.expire(test_key, 60)
        self.assertTrue(result)
        self.cache._redis.expire.assert_called_once()
    
    def test_clear(self):
        """Test clear operation"""
        # Mock Redis keys and delete
        self.cache._redis.keys.return_value = [b"pythoncode:key1", b"pythoncode:key2"]
        self.cache._redis.delete.return_value = 2
        
        deleted = self.cache.clear("*")
        self.assertEqual(deleted, 2)
        self.cache._redis.keys.assert_called_once()
        self.cache._redis.delete.assert_called_once()
    
    def test_get_stats(self):
        """Test statistics collection"""
        stats = self.cache.get_stats()
        
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('sets', stats)
        self.assertIn('deletes', stats)
        self.assertIn('errors', stats)
        self.assertIn('hit_rate', stats)
    
    def test_reset_stats(self):
        """Test statistics reset"""
        # Set some stats
        self.cache.stats['hits'] = 10
        self.cache.stats['misses'] = 5
        
        self.cache.reset_stats()
        
        self.assertEqual(self.cache.stats['hits'], 0)
        self.assertEqual(self.cache.stats['misses'], 0)


class TestCacheDecorators(unittest.TestCase):
    """Test cache decorators"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock cache manager
        self.cache = CacheManager()
        self.cache._redis = Mock()
        self.cache._is_connected = Mock(return_value=True)
        self.cache.get = Mock()
        self.cache.set = Mock()
    
    def test_cache_function_decorator(self):
        """Test function caching decorator"""
        # Create a test function
        call_count = 0
        
        @self.cache.cache_function(ttl=30)
        def test_func(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # Mock cache behavior
        self.cache.get.return_value = None  # First call: cache miss
        self.cache.set.return_value = True
        
        # First call - should compute
        result1 = test_func(5, 3)
        self.assertEqual(result1, 8)
        self.assertEqual(call_count, 1)
        self.cache.get.assert_called_once()
        self.cache.set.assert_called_once()
        
        # Reset mocks for second call
        self.cache.get.reset_mock()
        self.cache.set.reset_mock()
        
        # Second call - should use cache
        self.cache.get.return_value = 8  # Cached value
        
        result2 = test_func(5, 3)
        self.assertEqual(result2, 8)
        self.assertEqual(call_count, 1)  # Function should not be called again
        self.cache.get.assert_called_once()
        self.cache.set.assert_not_called()  # Should not set cache again
    
    def test_cache_method_decorator(self):
        """Test method caching decorator"""
        # Create a test class
        class TestClass:
            def __init__(self, value):
                self.value = value
                self.call_count = 0
            
            @self.cache.cache_method(ttl=30)
            def compute(self, x):
                self.call_count += 1
                return self.value + x
        
        # Create instance
        instance = TestClass(10)
        
        # Mock cache behavior
        self.cache.get.return_value = None  # First call: cache miss
        self.cache.set.return_value = True
        
        # First call - should compute
        result1 = instance.compute(5)
        self.assertEqual(result1, 15)
        self.assertEqual(instance.call_count, 1)
        self.cache.get.assert_called_once()
        self.cache.set.assert_called_once()
        
        # Reset mocks for second call
        self.cache.get.reset_mock()
        self.cache.set.reset_mock()
        
        # Second call - should use cache
        self.cache.get.return_value = 15  # Cached value
        
        result2 = instance.compute(5)
        self.assertEqual(result2, 15)
        self.assertEqual(instance.call_count, 1)  # Method should not be called again
        self.cache.get.assert_called_once()
        self.cache.set.assert_not_called()  # Should not set cache again


class TestGlobalCache(unittest.TestCase):
    """Test global cache functions"""
    
    @patch('utils.cache_manager.CacheManager')
    def test_get_cache_manager(self, mock_cache_class):
        """Test getting global cache manager"""
        from utils.cache_manager import get_cache_manager, _cache_instance
        
        # Reset global instance
        import utils.cache_manager
        utils.cache_manager._cache_instance = None
        
        # Get cache manager
        cache1 = get_cache_manager()
        
        # Should create new instance
        mock_cache_class.assert_called_once()
        
        # Get cache manager again
        cache2 = get_cache_manager()
        
        # Should return same instance
        self.assertIs(cache1, cache2)
    
    def test_cache_function_decorator_global(self):
        """Test global cache function decorator"""
        from utils.cache_manager import cache_function
        
        # Mock the global cache
        mock_cache = Mock()
        mock_cache.cache_function.return_value = lambda func: func
        
        with patch('utils.cache_manager.get_cache_manager', return_value=mock_cache):
            # Apply decorator
            @cache_function(ttl=60)
            def test_func():
                return "result"
            
            # Verify cache_function was called on cache manager
            mock_cache.cache_function.assert_called_once_with(60, 'func:')
    
    def test_cache_method_decorator_global(self):
        """Test global cache method decorator"""
        from utils.cache_manager import cache_method
        
        # Mock the global cache
        mock_cache = Mock()
        mock_cache.cache_method.return_value = lambda method: method
        
        with patch('utils.cache_manager.get_cache_manager', return_value=mock_cache):
            # Apply decorator
            class TestClass:
                @cache_method(ttl=60)
                def test_method(self):
                    return "result"
            
            # Verify cache_method was called on cache manager
            mock_cache.cache_method.assert_called_once_with(60, 'method:')


class TestCacheManagerDisconnected(unittest.TestCase):
    """Test CacheManager when Redis is disconnected"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = CacheManager()
        self.cache._redis = None
        self.cache._is_connected = Mock(return_value=False)
    
    def test_get_when_disconnected(self):
        """Test get when Redis is disconnected"""
        result = self.cache.get("test_key", "default")
        self.assertEqual(result, "default")
    
    def test_set_when_disconnected(self):
        """Test set when Redis is disconnected"""
        result = self.cache.set("test_key", "value")
        self.assertFalse(result)
    
    def test_delete_when_disconnected(self):
        """Test delete when Redis is disconnected"""
        result = self.cache.delete("test_key")
        self.assertFalse(result)
    
    def test_exists_when_disconnected(self):
        """Test exists when Redis is disconnected"""
        result = self.cache.exists("test_key")
        self.assertFalse(result)
    
    def test_clear_when_disconnected(self):
        """Test clear when Redis is disconnected"""
        result = self.cache.clear("*")
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)