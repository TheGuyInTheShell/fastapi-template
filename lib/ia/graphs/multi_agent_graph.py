from langgraph.graph import StateGraph, END
from .state import AgentState
from ..nodes.agent_nodes import researcher_node, writer_node
from ..agents.supervisor import supervisor_agent

def create_multi_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("Researcher", researcher_node)
    workflow.add_node("Writer", writer_node)
    
    # Add supervisor logic
    async def supervisor_logic(state: AgentState):
        result = await supervisor_agent.ainvoke(state)
        return {"next": result.next_step}
        
    workflow.add_node("supervisor", supervisor_logic)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "Researcher": "Researcher",
            "Writer": "Writer",
            "Finish": END
        }
    )
    
    # Add normal edges back to supervisor
    workflow.add_edge("Researcher", "supervisor")
    workflow.add_edge("Writer", "supervisor")
    
    return workflow.compile()

multi_agent_graph = create_multi_agent_graph()
