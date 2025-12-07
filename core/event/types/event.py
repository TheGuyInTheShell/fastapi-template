from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Literal, Set, Tuple, Union, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    from .channel_event import ABCChannelEvent

TAction = Literal["before", "after"]

class ABCEvent(ABC):

    def __init__(self):

        self._before_listeners: Set[Callable] = set()

        self._after_listeners: Set[Callable] = set()

    @abstractmethod
    def add_listener(self, action: TAction, handler: Callable):

        pass
    
    @abstractmethod
    def add_action(self, action: TAction, handler: Callable):

        pass
    
    @abstractmethod
    def remove_listener(self, handler: Callable, action: Union[TAction, None]):

        pass
    
    @abstractmethod
    def remove_action(self, handler: Callable, action: TAction):

        pass
    
    @abstractmethod
    def get_after_listeners(self) -> Set[Callable]:

        pass
    
    @abstractmethod
    def get_before_listeners(self) -> Set[Callable]:

        pass
    
    @abstractmethod
    def prepare(self, channelRef: "ABCChannelEvent") -> "ABCEvent":

        pass
    
    @abstractmethod
    def run(self, *args, **kwargs) -> "ABCEvent":

        pass