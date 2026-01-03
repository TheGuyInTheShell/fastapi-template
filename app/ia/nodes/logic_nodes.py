import operator
from typing import Annotated, Sequence, TypedDict, Union
from langchain_core.messages import BaseMessage
from typing import Dict, Any, Literal

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    # Placeholder for supervisor logic which is handled by the agent usually
    return {"next": "continue"}

def should_continue(state: AgentState) -> Union[str, Literal["__end__"]]:
    last_message = state["messages"][-1]
    if "FINISH" in last_message.content:
        return "__end__"
    return "continue"
