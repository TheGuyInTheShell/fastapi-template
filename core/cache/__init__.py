from core.config.globals import settings
import json
import inspect
from functools import wraps
from typing import Any, Optional, Callable

# Import Backends
from .base import BaseCacheBackend
from .memory import InMemoryCacheBackend

# Try to import Redis backend, but don't fail if dependencies are issues (though we know they exist)
from .redis.backend import RedisCacheBackend


class Cache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.backend: BaseCacheBackend | None = None

        # Configuration
        redis_host = settings.REDIS_HOST
        redis_port = settings.REDIS_PORT

        # Try to initialize Redis
        try:
            self.backend = RedisCacheBackend(host=redis_host, port=redis_port)
        except Exception as e:
            print(
                f"Cache Warning: Could not connect to Redis ({e}). Falling back to In-Memory."
            )
            self.backend = InMemoryCacheBackend()

    # --- Public Accessors for manual usage ---

    async def get(self, key: str) -> Any:
        try:
            if self.backend is None:
                return None
            return await self.backend.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        try:
            if self.backend is None:
                return
            await self.backend.set(key, value, ttl)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        try:
            if self.backend is None:
                return
            await self.backend.delete(key)
        except Exception:
            pass

    def sync_get(self, key: str) -> Any:
        try:
            if self.backend is None:
                return None
            return self.backend.sync_get(key)
        except Exception:
            return None

    def sync_set(self, key: str, value: Any, ttl: int = 60) -> None:
        try:
            if self.backend is None:
                return
            self.backend.sync_set(key, value, ttl)
        except Exception:
            pass

    def sync_delete(self, key: str) -> None:
        try:
            if self.backend is None:
                return
            self.backend.sync_delete(key)
        except Exception:
            pass

    # --- Decorators ---

    def cache_endpoint(self, ttl: int = 60, namespace: str = "main"):
        """
        Caching decorator for FastAPI endpoints. Supports Sync and Async functions.
        """

        def decorator(func):
            is_async = inspect.iscoroutinefunction(func)

            def generate_key(args, kwargs, func_name):
                user_id = kwargs.get("user_id")
                parts = [namespace]
                if user_id:
                    parts.append(f"user:{user_id}")
                else:
                    parts.append(func_name)
                    key_data = json.dumps(
                        {
                            "args": [str(a) for a in args],
                            "kwargs": {k: str(v) for k, v in kwargs.items()},
                        },
                        sort_keys=True,
                    )
                    parts.append(key_data)
                return ":".join(parts)

            if is_async:

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    cache_key = generate_key(args, kwargs, func.__name__)

                    # Try Cache (Accessing self via closure is tricky if methods are bound)
                    # Use self since this is an instance method
                    try:
                        cached = await self.get(cache_key)
                        if cached:
                            try:
                                return json.loads(cached)
                            except:
                                pass
                    except Exception:
                        pass

                    response = await func(*args, **kwargs)

                    try:
                        if isinstance(response, dict):
                            val = json.dumps(response)
                            await self.set(cache_key, val, ttl=ttl)
                    except Exception:
                        pass

                    return response

                return async_wrapper

            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    cache_key = generate_key(args, kwargs, func.__name__)

                    try:
                        cached = self.sync_get(cache_key)
                        if cached:
                            try:
                                return json.loads(cached)
                            except:
                                return cached
                    except Exception:
                        pass

                    response = func(*args, **kwargs)

                    try:
                        if isinstance(response, dict):
                            val = json.dumps(response)
                        else:
                            val = response
                        self.sync_set(cache_key, val, ttl=ttl)
                    except Exception:
                        pass

                    return response

                return sync_wrapper

        return decorator

    def cache_db(self, ttl: int = 60, prefix: str = "db"):
        """
        Caching decorator explicitly for DB functions (Services/Repositories).
        """

        def decorator(func):
            is_async = inspect.iscoroutinefunction(func)

            def generate_key(args, kwargs, func_name):
                parts = [prefix, func_name]
                key_data = json.dumps(
                    {
                        "args": [str(a) for a in args],
                        "kwargs": {k: str(v) for k, v in kwargs.items()},
                    },
                    sort_keys=True,
                )
                parts.append(key_data)
                return ":".join(parts)

            if is_async:

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    cache_key = generate_key(args, kwargs, func.__name__)

                    try:
                        cached = await self.get(cache_key)
                        if cached:
                            try:
                                return json.loads(cached)
                            except:
                                pass
                    except Exception:
                        pass

                    response = await func(*args, **kwargs)

                    try:
                        val = self._serialize_db_response(response)
                        if val:
                            await self.set(cache_key, val, ttl=ttl)
                    except Exception:
                        pass

                    return response

                return async_wrapper
            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    cache_key = generate_key(args, kwargs, func.__name__)

                    try:
                        cached = self.sync_get(cache_key)
                        if cached:
                            try:
                                return json.loads(cached)
                            except:
                                pass
                    except Exception:
                        pass

                    response = func(*args, **kwargs)

                    try:
                        val = self._serialize_db_response(response)
                        if val:
                            self.sync_set(cache_key, val, ttl=ttl)
                    except Exception:
                        pass

                    return response

                return sync_wrapper

        return decorator

    def _serialize_db_response(self, response: Any) -> Optional[str]:
        if hasattr(response, "model_dump"):
            return json.dumps(response.model_dump())
        elif hasattr(response, "dict"):
            return json.dumps(response.dict())
        elif isinstance(response, dict):
            return json.dumps(response)
        elif isinstance(response, (list, tuple)):
            data_list = []
            for item in response:
                if hasattr(item, "model_dump"):
                    data_list.append(item.model_dump())
                elif hasattr(item, "dict"):
                    data_list.append(item.dict())
                else:
                    data_list.append(item)
            return json.dumps(data_list)
        return None


# Singleton Instance
cache = Cache()

# Expose decorators as if they were top-level functions for backward compatibility
# The user's previous code imports `cache_endpoint`.
# While proper object-oriented usage is `@cache.cache_endpoint`, to prevent
# breaking ALL files I changed, I will alias them here.
# Warning: This binds the decorator to the singleton instance 'cache'.

cache_endpoint = cache.cache_endpoint
cache_db = cache.cache_db
