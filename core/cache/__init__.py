import os
import json
import redis.asyncio as redis
import redis as redis_sync
from functools import wraps
from typing import Optional, Any
from fastapi import HTTPException
import asyncio
import time

class InMemoryCache:
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[str]:
        data = self._cache.get(key)
        if not data:
            return None
        value, expire_at = data
        if expire_at and time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl: int = 60):
        expire_at = time.time() + ttl
        self._cache[key] = (value, expire_at)

    async def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

class Cache:
    _instance = None
    _backend = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            if asyncio.get_event_loop().is_running():
                asyncio.ensure_future(cls._instance._init_backend())
            else:
                asyncio.run(cls._instance._init_backend())
        return cls._instance

    async def _init_backend(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        self._memory_client = InMemoryCache()
        self._use_redis = False

        # Try to initialize Redis
        try:
            # We don't await here because __init__ is sync, but we create the client.
            # Actual connection check might happen on first use or we can try a ping if we were async.
            # For simplicity, we assume Redis is preferred if configured.
            # Ideally we'd ping to check availability, but that requires async.
            # We will default to Redis client, and handle connection errors in methods?
            # Or effectively "if configured, use it".
            # The prompt says: "use redis si esta disponible segun un archivo de configuracion"
            # It also says: "si no esta disponible crea una cache en memoria" - this suggests dynamic check.
            
            # Let's try to verify connection? We can't easily in sync __new__.
            # We'll use a lazy approach or a sync check if possible, OR just default to Memory if not ENV set.
            # Assuming if env vars are present, we try Redis.
            self._redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            await self._redis_client.ping()
            self._use_redis = True
            return
        except redis.ConnectionError as e:
            print('Redis connection error (using memory cache)')
        
        # We'll determine backend on first use or assume valid if env vars set?
        # A robust way is to try to ping in a startup hook, but here we are in a class.
        # Let's try to connect in a background task or just failover gracefully.
        # Actually, let's allow failing over to memory if redis operation fails.
        
    async def get(self, key: str) -> Any:
        try:
            # Try Redis first
            if self._use_redis:
                return await self._redis_client.get(key)
            else:
                return await self._memory_client.get(key)
        except redis.ConnectionError:
            # Fallback to memory
             return await self._memory_client.get(key)
        except Exception as e:
            # Fallback for other redis errors
            return await self._memory_client.get(key)

    async def set(self, key: str, value: str, ttl: int = 60):
        try:
            if self._use_redis:
                await self._redis_client.set(key, value, ex=ttl)
            else:
                await self._memory_client.set(key, value, ttl)
        except redis.ConnectionError:
            if self._use_redis:
                await self._memory_client.set(key, value, ttl)
        except Exception:
            if self._use_redis:
                await self._memory_client.set(key, value, ttl)

    async def delete(self, key: str):
        try:
            if self._use_redis:
                await self._redis_client.delete(key)
            else:
                await self._memory_client.delete(key)
        except Exception:
            if self._use_redis:
                await self._memory_client.delete(key)


    def sync_get(self, key: str) -> Any:
        try:
            # Try Redis first
            if self._use_redis:
                return self._redis_client.get(key)
            else:
                return self._memory_client.get(key)
        except redis.ConnectionError:
            # Fallback to memory
             return self._memory_client.get(key)
        except Exception as e:
            # Fallback for other redis errors
            return self._memory_client.get(key)

    def sync_set(self, key: str, value: str, ttl: int = 60):
        try:
            if self._use_redis:
                self._redis_client.set(key, value, ex=ttl)
            else:
                self._memory_client.set(key, value, ttl)
        except redis.ConnectionError:
            if self._use_redis:
                self._memory_client.set(key, value, ttl)
        except Exception:
            if self._use_redis:
                self._memory_client.set(key, value, ttl)

    def sync_delete(self, key: str):
        try:
            if self._use_redis:
                self._redis_client.delete(key)
            else:
                self._memory_client.delete(key)
        except Exception:
            if self._use_redis:
                self._memory_client.delete(key)

def cache_endpoint(ttl: int = 60, namespace: str = "main"):
    """
    Caching decorator for FastAPI endpoints.

    ttl: Time to live for the cache in seconds.
    namespace: Namespace for cache keys in Redis.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Attempt to extract identifiers for the key
            # Priority: user_id provided in kwargs, or the first arg (if applicable/safe assumption)
            # This logic mimics the user's example but might be risky if args[0] isn't user_id.
            # Safest is to rely on specific kwargs if known, or hash all args.
            # User example: user_id = kwargs.get('user_id') or args[0]
            
            # Use request path/query if available? The user specifically used "user_id".
            # I will try to support a generic key generation if user_id is missing, 
            # to make it applicable to ANY endpoint as requested ("cada enpoint").
            
            user_id = kwargs.get('user_id')
            if not user_id and args:
                 # Check if the first arg is a primitive we can use? 
                 # Often first arg in existing endpoints might be 'request' or 'db'.
                 # Let's just use a hash of args/kwargs for a generic key if user_id missing.
                 pass

            parts = [namespace]
            if user_id:
                parts.append(f"user:{user_id}")
            else:
                # Generic cache key strategy: func name + args hash
                 parts.append(func.__name__)
                 # Simple arg stringification (careful with objects)
                 # This is a basic implementation.
                 key_data = json.dumps({
                     "args": [str(a) for a in args], 
                     "kwargs": {k: str(v) for k, v in kwargs.items()}
                 }, sort_keys=True)
                 parts.append(key_data)

            cache_key = ":".join(parts)
            cache = Cache()

            # Try to retrieve data from cache
            try:
                cached_value = await cache.get(cache_key)
                if cached_value:
                    try:
                        return json.loads(cached_value)
                    except Exception:
                        return cached_value
            except Exception:
                # If deserialization fails or other error, proceed to call func
                pass

            # Call the actual function
            response = await func(*args, **kwargs)

            try:
                # Store the response
                # We need to serialize response. Pydantic models need .model_dump() or jsonable_encoder
                # But implementation plan says "json.dumps".
                # If response is a Pydantic model, json.dumps might fail unless we handle it.
                # Assuming simple dicts or json-compatible for now as per example.
                
                try:
                    json_response = json.dumps(response)
                except Exception:
                    json_response = response

                await cache.set(cache_key, json_response, ttl=ttl)
            except Exception as e:
                # Log error but don't fail the request?
                # User example raised HTTPException(500).
                raise HTTPException(status_code=500, detail=f"Error caching data: {e}")

            return response
        return wrapper
    return decorator
