import os
import json
import redis.asyncio as redis
import redis as redis_sync
from functools import wraps
from typing import Optional, Any
from fastapi import HTTPException
import asyncio
import time
import inspect

class InMemoryCache:
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[str]:
        return self._get_sync(key)

    def _get_sync(self, key: str) -> Optional[str]:
        data = self._cache.get(key)
        if not data:
            return None
        value, expire_at = data
        if expire_at and time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl: int = 60):
        self._set_sync(key, value, ttl)

    def _set_sync(self, key: str, value: str, ttl: int = 60):
        expire_at = time.time() + ttl
        self._cache[key] = (value, expire_at)

    async def delete(self, key: str):
        self._delete_sync(key)

    def _delete_sync(self, key: str):
        if key in self._cache:
            del self._cache[key]

class Cache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._redis_host = os.getenv("REDIS_HOST", "localhost")
        self._redis_port = int(os.getenv("REDIS_PORT", 6379))
        self._memory_client = InMemoryCache()
        self._use_redis = False
        self._async_redis_client = None
        self._sync_redis_client = None

        # Initialize Sync Client Immediately
        try:

            # Initialize Async Client (Fire and forget, or wait if loop running)
            self._async_redis_client = redis.Redis(
                host=self._redis_host,
                port=self._redis_port,
                decode_responses=True
            )

            self._sync_redis_client = redis_sync.Redis(
                host=self._redis_host,
                port=self._redis_port,
                decode_responses=True
            )
            self._sync_redis_client.ping()

            self._use_redis = True
        except Exception:
            # Fallback to memory if initial ping fails
            pass
        

    # --- Async Methods ---
    async def get(self, key: str) -> Any:
        try:
            if self._use_redis:
                return await self._async_redis_client.get(key)
            return await self._memory_client.get(key)
        except Exception:
            return await self._memory_client.get(key)

    async def set(self, key: str, value: str, ttl: int = 60):
        try:
            if self._use_redis:
                await self._async_redis_client.set(key, value, ex=ttl)
            else:
                await self._memory_client.set(key, value, ttl)
        except Exception:
            await self._memory_client.set(key, value, ttl)

    async def delete(self, key: str):
        try:
            if self._use_redis:
                await self._async_redis_client.delete(key)
            else:
                await self._memory_client.delete(key)
        except Exception:
             await self._memory_client.delete(key)

    # --- Sync Methods ---
    def sync_get(self, key: str) -> Any:
        try:
            if self._use_redis:
                return self._sync_redis_client.get(key)
            return self._memory_client._get_sync(key)
        except Exception:
             return self._memory_client._get_sync(key)

    def sync_set(self, key: str, value: str, ttl: int = 60):
        try:
            if self._use_redis:
                self._sync_redis_client.set(key, value, ex=ttl)
            else:
                self._memory_client._set_sync(key, value, ttl)
        except Exception:
            self._memory_client._set_sync(key, value, ttl)

    def sync_delete(self, key: str):
        try:
            if self._use_redis:
                self._sync_redis_client.delete(key)
            else:
                self._memory_client._delete_sync(key)
        except Exception:
            self._memory_client._delete_sync(key)

def cache_endpoint(ttl: int = 60, namespace: str = "main"):
    """
    Caching decorator for FastAPI endpoints. Supports Sync and Async functions.
    """
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)
        
        def generate_key(args, kwargs, func_name):
            user_id = kwargs.get('user_id')
            parts = [namespace]
            if user_id:
                parts.append(f"user:{user_id}")
            else:
                 parts.append(func_name)
                 key_data = json.dumps({
                     "args": [str(a) for a in args], 
                     "kwargs": {k: str(v) for k, v in kwargs.items()}
                 }, sort_keys=True)
                 parts.append(key_data)
            return ":".join(parts)

        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = generate_key(args, kwargs, func.__name__)
                cache = Cache()

                # Try Cache
                try:
                    cached = await cache.get(cache_key)
                    if cached:
                        try:
                            return json.loads(cached)
                        except:
                            pass
                except Exception:
                    pass

                # Call original
                response = await func(*args, **kwargs)

                # Store Cache
                try:
                    if isinstance(response, dict):
                        val = json.dumps(response)
                        await cache.set(cache_key, val, ttl=ttl)
                except Exception as e:
                    pass
                
                return response
            return async_wrapper
            
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = generate_key(args, kwargs, func.__name__)
                cache = Cache()

                # Try Cache
                try:
                    cached = cache.sync_get(cache_key)
                    if cached:
                        try:
                            return json.loads(cached)
                        except:
                            return cached
                except Exception:
                    pass

                # Call original
                response = func(*args, **kwargs)

                # Store Cache
                try:
                    if isinstance(response, dict):
                        val = json.dumps(response)
                    else:
                        val = response
                    cache.sync_set(cache_key, val, ttl=ttl)
                except Exception as e:
                    pass
                
                return response
            return sync_wrapper
            
    return decorator
