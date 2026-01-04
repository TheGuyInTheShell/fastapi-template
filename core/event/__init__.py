import asyncio
import inspect

from asyncio import iscoroutinefunction
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Set,
    Tuple,
    Union,
    Awaitable,
    TYPE_CHECKING,
    Optional,
    Iterator
)
from .base.event import Event
from .utils.type_check import type_check
from .types.channel_event import ABCChannelEvent, ABCEvent


if TYPE_CHECKING:
    from .base.event import TAction


class EventDependency:
    def __init__(self, dependency: Callable):
        self.dependency = dependency

# interator injection of result
def event_result(event: "ABCEvent"):
    try:
        return event.result
    except NameError:
        return None
    


class ChannelEvent(ABCChannelEvent):

    events: Dict[str, ABCEvent] = {}

    instances = None

    def __new__(cls):
        if not cls.instances:

            cls.instances = super(ChannelEvent, cls).__new__(cls)
        return cls.instances

    def __init__(self):
        # Override to prevent ABCChannelEvent.__init__ from resetting self.events
        pass
        


    async def _call_listeners(
        self, listeners: Set[Callable], args: Tuple, kwargs: Dict, event: "ABCEvent"
    ):
        for listener in listeners:
            sig = inspect.signature(listener)
            target_kwargs = {}

            # Check for generic **kwargs
            has_var_kwargs = any(
                p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
            )

            # Handle regular params and DependsEvent
            for name, param in sig.parameters.items():
                if isinstance(param.default, EventDependency):
                     # dependency logic
                     dep_res = param.default.dependency(event)
                     target_kwargs[name] = dep_res
                elif name in kwargs:
                    target_kwargs[name] = kwargs[name]
                
            if has_var_kwargs:
                # Add remaining kwargs if **kwargs exists
                for k, v in kwargs.items():
                    if k not in target_kwargs:
                        target_kwargs[k] = v

            (
                await listener(*args, **target_kwargs)
                if iscoroutinefunction(listener)
                else listener(*args, **target_kwargs)
            )

    async def _iterator(self, event: "ABCEvent", func: Callable, *args, **kwargs):

        result = None

        await self._call_listeners(
            listeners=event._before_listeners, args=args, kwargs=kwargs, event=event
        )

        result = (
            await func(*args, **kwargs)
            if iscoroutinefunction(func)
            else func(*args, **kwargs)
        )

        event.result = result

        await self._call_listeners(
            listeners=event._after_listeners, args=args, kwargs=kwargs, event=event
        )

        event.result = None

        return result

    def DependsEvent(self, dependency: Callable):
        return EventDependency(dependency)

    def with_args_types(self, event: "ABCEvent"):

        def meta_decorator(*args_types, **kwargs_types):

            def decorator(
                func: Union[Callable[..., Any], Callable[..., Awaitable]],
            ) -> Any:

                def wrapper(*args, **kwargs):

                    type_check(args_types, kwargs_types, args, kwargs)

                    result = self._iterator(event, func, *args, **kwargs)
                    return result

                return wrapper

            return decorator

        return meta_decorator

    def listen_to(self, event_key: str):
        """



        listen a the execution of a function and emit to an event



        """

        self.events[event_key] = Event()

        event = self.events[event_key]

        return self.with_args_types(event)

    def subscribe_to(
        self,
        event_key: str,
        action: "TAction" = "before",
        handler: Union[Callable[..., Any], Callable[..., Awaitable]] | None = None,
    ) -> Callable[..., Any]:
        """

        subscribe to an event

        """

        def decorator(
            handler: Union[Callable[..., Any], Callable[..., Awaitable]],
        ) -> Any:

            event: "ABCEvent" | None = self.events.get(event_key)

            # If event not found create it

            if event is None:

                event = Event()

                self.events[event_key] = event

            event.add_listener(action, handler)

            def wrapper(*args, **kwargs):

                return handler(*args, **kwargs)

            return wrapper

        if handler is None:

            # if handler is not passed, return decorator
            return decorator
        else:

            # if handler is passed, return decorator with handler

            return decorator(handler)

    def emit_to(self, event_key: str) -> "ABCEvent":
        """

        forced emit to event_key

        """

        event: "ABCEvent" | None = self.events.get(event_key)

        if event is None:

            event = Event()

            self.events[event_key] = event

        try:


            return event.prepare(self)

        except Exception as e:
            raise e


if __name__ == "__main__":

    async def test():

        channel = ChannelEvent()

        @channel.listen_to("test")(int, int, c=int, d=int)
        async def test_func(a, b, c, d):

            return a + b + c + d

        channel.subscribe_to(
            "test", "after", lambda *args, **kwargs: print(args, kwargs)
        )

        await test_func(1, 2, c=1, d=2)

        channel.emit_to("test").run(1, 2)

    asyncio.run(test())
