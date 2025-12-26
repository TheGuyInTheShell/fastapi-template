import asyncio

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
)
from .base.event import Event
from .utils.type_check import type_check
from .types.channel_event import ABCChannelEvent


if TYPE_CHECKING:
    from .base.event import TAction


class ChannelEvent(ABCChannelEvent):

    events: Dict[str, Event] = dict()

    instances = None

    def __new__(cls):
        if not cls.instances:

            cls.instances = super(ChannelEvent, cls).__new__(cls)
        return cls.instances

    async def _call_listeners(
        self, listeners: Set[Callable], args: Tuple, kwargs: Dict
    ):
        for listener in listeners:

            (
                await listener(*args, **kwargs)
                if iscoroutinefunction(listener)
                else listener(*args, **kwargs)
            )

    async def _iterator(self, event: Event, func: Callable, *args, **kwargs):

        result = None

        await self._call_listeners(
            listeners=event._before_listeners, args=args, kwargs=kwargs
        )

        result = (
            await func(*args, **kwargs)
            if iscoroutinefunction(func)
            else func(*args, **kwargs)
        )

        kwargs.update({"result": result})

        await self._call_listeners(
            listeners=event._after_listeners, args=args, kwargs=kwargs
        )
        return result

    def with_args_types(self, event: Event):

        def meta_decorator(*args_types, **kwargs_types):

            def decorator(
                func: Union[Callable[..., Any], Callable[..., Awaitable]],
            ) -> any:

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
        handler: Union[Callable[..., Any], Callable[..., Awaitable]] = None,
    ) -> Callable[..., Any]:
        """

        subscribe to an event

        """

        def decorator(
            handler: Union[Callable[..., Any], Callable[..., Awaitable]],
        ) -> any:

            event: Event = self.events.get(event_key)

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

    def emit_to(self, event_key: str) -> Event:
        """



        forced emit to event_key



        """

        event: Event = self.events.get(event_key)

        if event is None:

            raise ValueError(f"Event {event_key} not found")

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
