import asyncio
from asyncio import iscoroutinefunction
from typing import Any, Callable, Dict, Literal, Set, Tuple, Union

from fastapi import BackgroundTasks

CallsType = Callable[[Tuple[Tuple, Dict, Any]], Any]

TAction = Literal["before", "after"]

class Event:
    _before_listeners: Set[Callable] = set()
    _after_listeners: Set[Callable] = set()

    def add_listener(self, action: TAction, handler: Callable):
        self.add_action(action, handler)
        return self

    def add_action(self, action: TAction, handler: Callable):
        if action == "before":
            self._before_listeners.add(handler)
        elif action == "after":
            self._after_listeners.add(handler)
        else:
            raise ValueError("Invalid action")

    def remove_listener(self, handler: Callable, action: Union[TAction, None]):
    

        if action is None:
            if handler in self._before_listeners:
                action = "before"
            elif handler in self._after_listeners:
                action = "after"
            else:
                raise ValueError("Handler not found")

        self.remove_action(handler, action)

        return self

    def remove_action(self, handler: Callable, action: TAction):

        if not handler in self._before_listeners and not handler in self._after_listeners:
            raise ValueError("Handler not found")

        if action == "before":
            self._before_listeners.remove(handler)
        elif action == "after":
            self._after_listeners.remove(handler)
        else:
            raise ValueError("Invalid action")

    def get_after_listeners(self) -> Set[Callable]:
        return self._after_listeners
    
    def get_before_listeners(self) -> Set[Callable]:
        return self._before_listeners


class ChannelEvent:
    events: Dict[str, Event] = dict()
    instances = None

    def __new__(cls):
        if not cls.instances:
            cls.instances = super(ChannelEvent, cls).__new__(cls)
        return cls.instances
    
    async def _call_listeners(self, listeners: Set[Callable], args: Tuple):
        for listener in listeners:
               await listener(args) if iscoroutinefunction(listener) else listener(args)
        

    async def _courutine_iterator(self, event: Event, func: Callable, *args, **kwargs):
        result = None
        asyncio.run(self._call_listeners(listeners=event._before_listeners,  args=(args, kwargs)))
        result = await func(*args, **kwargs)
        kwargs.update({"result": result})
        asyncio.run(self._call_listeners(listeners=event._after_listeners, args=(args, kwargs, result)))
        return result
        

    def _iterator(self, event: Event, func: Callable, *args, **kwargs):
        result = None
        asyncio.run(self._call_listeners(listeners=event._before_listeners, args=(args, kwargs)))
        result = func(*args, **kwargs)
        asyncio.run(self._call_listeners(listeners=event._after_listeners, args=(args, kwargs, result)))
        return result
    

    def listen(self, event_key: str):
        self.events[event_key] = Event()
        event = self.events[event_key]
        
        def decorator(func: Callable[..., Any]) -> any:
            
            def wrapper(*args, **kwargs):
                result = self._courutine_iterator(event, func, *args, **kwargs) if iscoroutinefunction(func) else self._iterator(event, func, *args, **kwargs)
                return result
            
            return wrapper
        
        return decorator


    def subscribe(self, event_key: str, action: TAction = "before", handler: Callable[..., Any] = None) -> Callable[..., Any]:
        
        def decorator(handler: Callable[..., Any]) -> any:
            
            event: Event = getattr(self.events, event_key, None)
            if event is None:
                event = Event()
                self.events[event_key] = event

            event.add_listener(action, handler)

            def wrapper(*args, **kwargs):
                return handler(*args, **kwargs)
            
            return wrapper
    
        if handler is None:
            # Si no se pasa una función, asumimos que se está llamando directamente
            return decorator
        else:
            # Si se pasa una función, se ejecuta como decorador
            return decorator(handler)

    def emit(self, event_key: str, *args, **kwargs):
        event: Event = self.events.get(event_key)
        if event is None:
            raise ValueError(f"Event {event_key} not found")
        def void(*args, **kwargs):
            pass
        return asyncio.run(self._courutine_iterator(event, void, *args, **kwargs)) if iscoroutinefunction(None) else self._iterator(event, void, *args, **kwargs)
        


# async def test():
#     channel = ChannelEvent()
#     @channel.listen("test")
#     async def test_func(a, b):
#         return a + b
#     channel.subscribe("test", Action(beforeCall=lambda x: print(x), afterCall=lambda x: print(x)))
#     await test_func(1, 2) 


# asyncio.run(test())