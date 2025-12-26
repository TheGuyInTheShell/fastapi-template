from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Set, Union, Awaitable
from .event import ABCEvent, TAction

CallsType = Callable[[tuple[tuple, dict, Any]], Any]


class ABCChannelEvent(ABC):

    def __init__(self):

        self.events: Dict[str, ABCEvent] = dict()

    @abstractmethod
    def emit_to(self, event_key: str):

        pass

    @abstractmethod
    def subscribe_to(
        self,
        event_key: str,
        action: TAction = "before",
        handler: Union[Callable[..., Any], Callable[..., Awaitable]] = None,
    ) -> Callable[..., Any]:

        pass

    @abstractmethod
    def listen_to(self, event_key: str):

        pass

    @abstractmethod
    def with_args_types(self, event: ABCEvent):

        pass
