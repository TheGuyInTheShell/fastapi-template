from langgraph.graph import StateGraph, END
from .state import AgentState
from ..nodes.agent_nodes import researcher_node, writer_node

def create_simple_flow_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("research", researcher_node)
    workflow.add_node("write", writer_node)
    
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", END)
    
    return workflow.compile()

simple_flow_graph = create_simple_flow_graph()
