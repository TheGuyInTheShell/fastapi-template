from functools import wraps
from typing import Any, List, Literal, Self, Sequence, Set

def make_hashable(value):
    if isinstance(value, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(make_hashable(v) for v in value)
    return value

def async_lru(maxsize=128):
    cache = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Filter out AsyncSession from args (it's usually the 2nd arg after cls, or explicitly passed)
            # Strategy: Generate key from strings of args, skipping AsyncSession objects
            key_args = []
            for arg in args:
                if "session.AsyncSession" in str(type(arg)) or "sqlalchemy.orm.session.Session" in str(type(arg)):
                    continue
                key_args.append(make_hashable(arg))
            
            key_kwargs = {k: make_hashable(v) for k, v in kwargs.items() if "session" not in str(type(v))}
            
            key = (func.__name__, tuple(key_args), tuple(sorted(key_kwargs.items())))
            
            if key in cache:
                return cache[key]
            
            result = await func(*args, **kwargs)
            
            if len(cache) >= maxsize:
                # Simple FIFO eviction for stability
                try:
                    cache.pop(next(iter(cache)))
                except StopIteration:
                    pass
            
            cache[key] = result
            return result
        return wrapper
    return decorator

def sync_lru(maxsize=128):
    cache = {}
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
             # Similar key generation
            key_args = tuple(make_hashable(arg) for arg in args)
            key_kwargs = tuple(sorted((k, make_hashable(v)) for k, v in kwargs.items()))
            key = (func.__name__, key_args, key_kwargs)
            
            if key in cache:
                return cache[key]
            
            result = func(*args, **kwargs)
            
            if len(cache) >= maxsize:
                 try:
                    cache.pop(next(iter(cache)))
                 except StopIteration:
                    pass
            
            cache[key] = result
            return result
        return wrapper
    return decorator
