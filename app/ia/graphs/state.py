import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Defines the shape of the state passed between nodes in the graph.
    """
    # Annotated with operator.add means messages will be appended
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # Tracks the next node to execute
    next: str
