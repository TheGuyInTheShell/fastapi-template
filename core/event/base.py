import asyncio

from asyncio import iscoroutinefunction

from typing import Any, Callable, Dict, Literal, Set, Tuple, Union, Awaitable


from fastapi import BackgroundTasks


CallsType = Callable[[Tuple[Tuple, Dict, Any]], Any]


TAction = Literal["before", "after"]


def type_verify(args_types, kwargs_types, args, kwargs):

    if len(args_types) != len(args):

        raise ValueError("Number of arguments does not match")

    if len(kwargs_types) != len(kwargs):

        raise ValueError("Number of keyword arguments does not match")

    for arg, arg_type in zip(args, args_types):

        if not isinstance(arg, arg_type):

            raise TypeError(f"Argument {arg} is not of type {arg_type}")

    for key, value in kwargs.items():
        if not isinstance(value, kwargs_types[key]):

            raise TypeError(f"Argument {key} is not of type {kwargs_types[key]}")


class Event:

    _before_listeners: Set[Callable]

    _after_listeners: Set[Callable]

    def __init__(self):

        self._before_listeners: Set[Callable] = set()

        self._after_listeners: Set[Callable] = set()


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

    event_target = ""

    event_args = []

    events_kwargs = {}

    instances = None


    def __new__(cls):
        if not cls.instances:

            cls.instances = super(ChannelEvent, cls).__new__(cls)
        return cls.instances
    

    async def _call_listeners(self, listeners: Set[Callable], args: Tuple, kwargs: Dict):
        for listener in listeners:

            await listener(*args, **kwargs) if iscoroutinefunction(listener) else listener(*args, **kwargs)
        


    async def _iterator(self, event: Event, func: Callable, *args, **kwargs):

        result = None

        await self._call_listeners(listeners=event._before_listeners, args=args, kwargs=kwargs)

        result = await func(*args, **kwargs) if iscoroutinefunction(func) else func(*args, **kwargs)
        kwargs.update({"result": result})
        await self._call_listeners(listeners=event._after_listeners, args=args, kwargs=kwargs)
        return result
    


    def with_args_types(self, event: Event):

        def meta_decorator(*args_types, **kwargs_types):

            def decorator(func: Union[Callable[..., Any], Callable[..., Awaitable]]) -> any:
                    

                def wrapper(*args, **kwargs):

                    type_verify(args_types, kwargs_types, args, kwargs)


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
        
        



    def subscribe_to(self, event_key: str, action: TAction = "before", handler: Union[Callable[..., Any], Callable[..., Awaitable]] = None) -> Callable[..., Any]:
        

        """
        

        subscribe to an event


        """
        

        def decorator(handler: Union[Callable[..., Any], Callable[..., Awaitable]]) -> any:
            

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


    def with_args(self, *args, **kwargs) -> Event:

        try:

            event: Event = self.events.get(self.event_target)

            self.event_args = args

            self.events_kwargs = kwargs
            return event

        except Exception as e:
            raise e

        finally:
            # Emit the event
            loop = asyncio.get_event_loop()
            loop.create_task(self._iterator(self.events.get(self.event_target), lambda *args, **kwargs: None, *self.event_args, **self.events_kwargs))
            self.event_args = []
            self.events_kwargs = {}
            self.event_target = ""


    def emit_to(self, event_key: str):


        """


        forced emit to event_key        


        """

        event: Event = self.events.get(event_key)

        if event is None:

            raise ValueError(f"Event {event_key} not found")

        try:

            self.event_target = event_key
            return self

        except Exception as e:
            raise e






if __name__ == "__main__":

    async def test():

        channel = ChannelEvent()

        @channel.listen_to("test")(int, int, c=int, d=int)
        async def test_func(a, b, c, d):

            return a + b + c + d

        channel.subscribe_to("test", "after", lambda *args, **kwargs: print(args, kwargs))

        await test_func(1, 2, c=1, d=2)

        channel.emit_to("test").with_args(1, 2)


    asyncio.run(test())