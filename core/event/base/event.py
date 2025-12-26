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
from ..types.event import ABCEvent

TAction = Literal["before", "after"]

if TYPE_CHECKING:
    from ..types.channel_event import ABCChannelEvent


class Event(ABCEvent):

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

        if (
            not handler in self._before_listeners
            and not handler in self._after_listeners
        ):

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

    def prepare(self, channelRef: "ABCChannelEvent") -> "Event":

        self.channelRef = channelRef

        return self

    def run(self, *args, **kwargs) -> "Event":

        try:

            self.event_args = args

            self.events_kwargs = kwargs

        except Exception as e:
            raise e

        finally:

            # Emit the event

            if asyncio.get_event_loop().is_running():

                asyncio.ensure_future(
                    self.channelRef._iterator(
                        self,
                        lambda *args, **kwargs: None,
                        *self.event_args,
                        **self.events_kwargs
                    )
                )
            else:

                asyncio.run(
                    self.channelRef._iterator(
                        self,
                        lambda *args, **kwargs: None,
                        *self.event_args,
                        **self.events_kwargs
                    )
                )

            self.event_args = []

            self.events_kwargs = {}

        return self
