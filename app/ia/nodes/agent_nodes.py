from typing import Dict, Any
from langchain_core.messages import HumanMessage
from ..agents.researcher import researcher_agent
from ..agents.writer import writer_agent

async def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])
    response = await researcher_agent.ainvoke({"messages": messages})
    return {"messages": [response]}

async def writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])
    response = await writer_agent.ainvoke({"messages": messages})
    return {"messages": [response]}
