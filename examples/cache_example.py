#!/usr/bin/env python3
"""
Example of using Cache Manager in PythonCode Project
"""

import time
from utils.cache_manager import CacheManager, cache_function, cache_method

def example_basic_cache():
    """Example of basic cache operations"""
    print("="*60)
    print("BASIC CACHE OPERATIONS")
    print("="*60)
    
    # Create cache manager
    cache = CacheManager()
    
    # Set values with different TTLs
    cache.set("user:1", {"id": 1, "name": "Alice", "email": "alice@example.com"}, ttl=300)
    cache.set("config:app", {"version": "1.0.0", "debug": False}, ttl=0)  # No expiration
    cache.set("temp:session", "session_data_123", ttl=60)
    
    print("Values set in cache")
    
    # Get values
    user = cache.get("user:1")
    config = cache.get("config:app")
    session = cache.get("temp:session")
    
    print(f"User: {user}")
    print(f"Config: {config}")
    print(f"Session: {session}")
    
    # Check if key exists
    exists = cache.exists("user:1")
    print(f"Key 'user:1' exists: {exists}")
    
    # Get TTL
    ttl = cache.ttl("user:1")
    print(f"TTL for 'user:1': {ttl} seconds")
    
    # Delete a key
    cache.delete("temp:session")
    print("Deleted 'temp:session'")
    
    # Clear all cache
    deleted = cache.clear("*")
    print(f"Cleared {deleted} keys from cache")
    
    # Get statistics
    stats = cache.get_stats()
    print(f"\nCache Statistics: {stats}")


def example_function_caching():
    """Example of function result caching"""
    print("\n" + "="*60)
    print("FUNCTION RESULT CACHING")
    print("="*60)
    
    cache = CacheManager()
    
    # Expensive computation function
    @cache.cache_function(ttl=30)
    def calculate_fibonacci(n):
        """Calculate Fibonacci number (expensive operation)"""
        print(f"Calculating Fibonacci({n})...")
        time.sleep(0.5)  # Simulate expensive computation
        
        if n <= 1:
            return n
        else:
            return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    
    # First call - will compute
    print("First call to calculate_fibonacci(10):")
    start = time.time()
    result1 = calculate_fibonacci(10)
    elapsed1 = time.time() - start
    print(f"Result: {result1}, Time: {elapsed1:.2f}s")
    
    # Second call - will use cache
    print("\nSecond call to calculate_fibonacci(10):")
    start = time.time()
    result2 = calculate_fibonacci(10)
    elapsed2 = time.time() - start
    print(f"Result: {result2}, Time: {elapsed2:.2f}s")
    
    # Different argument - will compute again
    print("\nCall to calculate_fibonacci(8):")
    start = time.time()
    result3 = calculate_fibonacci(8)
    elapsed3 = time.time() - start
    print(f"Result: {result3}, Time: {elapsed3:.2f}s")
    
    print(f"\nPerformance improvement: {elapsed1/elapsed2:.1f}x faster with cache!")


def example_method_caching():
    """Example of method result caching"""
    print("\n" + "="*60)
    print("METHOD RESULT CACHING")
    print("="*60)
    
    cache = CacheManager()
    
    class UserService:
        """Example service with cached methods"""
        
        def __init__(self, cache_manager):
            self.cache = cache_manager
            self.db_call_count = 0
        
        @cache.cache_method(ttl=60)
        def get_user_by_id(self, user_id):
            """Get user from database (simulated)"""
            print(f"Fetching user {user_id} from database...")
            self.db_call_count += 1
            time.sleep(0.3)  # Simulate database query
            
            # Simulated database response
            users = {
                1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
                2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
                3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            }
            
            return users.get(user_id)
        
        @cache.cache_method(ttl=300)
        def get_user_stats(self, user_id):
            """Get user statistics (expensive calculation)"""
            print(f"Calculating stats for user {user_id}...")
            time.sleep(0.5)  # Simulate expensive calculation
            
            return {
                "user_id": user_id,
                "active_days": 42,
                "total_actions": 1234,
                "last_active": "2024-01-15"
            }
    
    # Create service instance
    service = UserService(cache)
    
    # First call - will query database
    print("First call to get_user_by_id(1):")
    start = time.time()
    user1 = service.get_user_by_id(1)
    elapsed1 = time.time() - start
    print(f"User: {user1}, Time: {elapsed1:.2f}s")
    print(f"Database calls: {service.db_call_count}")
    
    # Second call - will use cache
    print("\nSecond call to get_user_by_id(1):")
    start = time.time()
    user2 = service.get_user_by_id(1)
    elapsed2 = time.time() - start
    print(f"User: {user2}, Time: {elapsed2:.2f}s")
    print(f"Database calls: {service.db_call_count} (should still be 1)")
    
    # Different user - will query database again
    print("\nCall to get_user_by_id(2):")
    start = time.time()
    user3 = service.get_user_by_id(2)
    elapsed3 = time.time() - start
    print(f"User: {user3}, Time: {elapsed3:.2f}s")
    print(f"Database calls: {service.db_call_count} (should be 2)")
    
    # Get user stats (cached separately)
    print("\nCall to get_user_stats(1):")
    stats = service.get_user_stats(1)
    print(f"Stats: {stats}")


def example_api_caching():
    """Example of API response caching"""
    print("\n" + "="*60)
    print("API RESPONSE CACHING")
    print("="*60)
    
    cache = CacheManager()
    
    # Simulated API responses
    def get_weather_data(city):
        """Simulate expensive API call to weather service"""
        print(f"Calling weather API for {city}...")
        time.sleep(1)  # Simulate API latency
        
        # Simulated API response
        weather_data = {
            "New York": {"temp": 72, "condition": "Sunny", "humidity": 65},
            "London": {"temp": 55, "condition": "Cloudy", "humidity": 80},
            "Tokyo": {"temp": 68, "condition": "Rainy", "humidity": 75}
        }
        
        return weather_data.get(city, {"temp": None, "condition": "Unknown", "humidity": None})
    
    # Cached version of API call
    def get_cached_weather(city, ttl=300):
        """Get weather data with caching"""
        cache_key = f"weather:{city.lower()}"
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print(f"Cache hit for {city}")
            cached_data["_cached"] = True
            return cached_data
        
        # Cache miss - call API
        print(f"Cache miss for {city}")
        data = get_weather_data(city)
        
        # Cache the result
        if data["temp"] is not None:  # Only cache valid responses
            cache.set(cache_key, data, ttl)
            data["_cached"] = False
        
        return data
    
    # Test cached API calls
    cities = ["New York", "London", "Tokyo", "New York", "London", "Paris"]
    
    print("Getting weather data for cities:")
    for city in cities:
        start = time.time()
        weather = get_cached_weather(city)
        elapsed = time.time() - start
        
        cached = weather.get("_cached", False)
        status = "CACHE HIT" if cached else "API CALL"
        
        print(f"  {city}: {weather['temp']}°F, {weather['condition']} "
              f"({status}, {elapsed:.2f}s)")
    
    # Show cache statistics
    stats = cache.get_stats()
    print(f"\nCache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']*100:.1f}%")


def example_cache_invalidation():
    """Example of cache invalidation strategies"""
    print("\n" + "="*60)
    print("CACHE INVALIDATION STRATEGIES")
    print("="*60)
    
    cache = CacheManager()
    
    # Simulate user data updates
    user_data = {
        "user:1": {"id": 1, "name": "Alice", "score": 100},
        "user:2": {"id": 2, "name": "Bob", "score": 200}
    }
    
    # Set initial cache
    for key, value in user_data.items():
        cache.set(key, value, ttl=3600)
    
    print("Initial cache state:")
    for key in user_data.keys():
        exists = cache.exists(key)
        print(f"  {key}: {'EXISTS' if exists else 'MISSING'}")
    
    # Strategy 1: Direct deletion
    print("\n1. Direct deletion:")
    cache.delete("user:1")
    print("  Deleted 'user:1' from cache")
    
    # Strategy 2: Pattern-based deletion
    print("\n2. Pattern-based deletion:")
    deleted = cache.clear("user:*")
    print(f"  Deleted {deleted} keys matching 'user:*'")
    
    # Strategy 3: Update with new TTL
    print("\n3. Update with new TTL:")
    cache.set("user:1", {"id": 1, "name": "Alice Updated", "score": 150}, ttl=60)
    print("  Updated 'user:1' with new data and 60s TTL")
    
    # Strategy 4: Version-based keys
    print("\n4. Version-based keys:")
    cache_version = "v2"
    cache.set(f"user:1:{cache_version}", {"id": 1, "name": "Alice v2"}, ttl=3600)
    print(f"  Set 'user:1:{cache_version}' with versioned key")
    
    # Check final state
    print("\nFinal cache state:")
    keys_to_check = ["user:1", "user:2", f"user:1:{cache_version}"]
    for key in keys_to_check:
        exists = cache.exists(key)
        print(f"  {key}: {'EXISTS' if exists else 'MISSING'}")


def main():
    """Run all examples"""
    print("CACHE MANAGER EXAMPLES")
    print("="*60)
    
    try:
        example_basic_cache()
        example_function_caching()
        example_method_caching()
        example_api_caching()
        example_cache_invalidation()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()