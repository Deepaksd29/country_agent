from langgraph.graph import StateGraph, START, END
from app.schema.state import AgentState
from app.agent.nodes import extract_intent, invoke_tool, synthesize_answer

def route_after_intent(state: AgentState) -> str:
    """Checks if we should continue to the tool or stop the graph."""
    if state.get("is_general_chat") or not state.get("is_supported"):
        return END
    return "tool_invocation"


def build_graph():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("intent_identification", extract_intent)
    builder.add_node("tool_invocation", invoke_tool)
    builder.add_node("answer_synthesis", synthesize_answer)
    

    builder.add_edge(START, "intent_identification")
    
    builder.add_conditional_edges(
        "intent_identification",
        route_after_intent,
        {
            "tool_invocation": "tool_invocation",
            END: END
        }
    )
    
    builder.add_edge("tool_invocation", "answer_synthesis")
    builder.add_edge("answer_synthesis", END)
    
    return builder.compile()