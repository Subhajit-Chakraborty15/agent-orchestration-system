from langgraph.graph import StateGraph, END
from app.orchestration.state import AgentState
from app.orchestration import supervisor
from app.orchestration.agents import researcher, coder, analyst
from app.escalation import escalation_manager


def specialist_dispatch(state: AgentState) -> str:
    """Conditional edge: send the state to whichever specialist the supervisor picked."""
    return state["route"]


def escalation_dispatch(state: AgentState) -> str:
    return "pause_for_human" if state["needs_approval"] else "release"


def release_node(state: AgentState) -> AgentState:
    state["final_answer"] = state["agent_output"]
    return state


def pause_node(state: AgentState) -> AgentState:
    # Graph execution stops here; the API layer persists this state and
    # waits for a human decision via POST /approvals/{id}/resolve
    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor.route)
    graph.add_node("researcher", researcher.run)
    graph.add_node("coder", coder.run)
    graph.add_node("analyst", analyst.run)
    graph.add_node("check_escalation", escalation_manager.check)
    graph.add_node("release", release_node)
    graph.add_node("pause_for_human", pause_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        specialist_dispatch,
        {"researcher": "researcher", "coder": "coder", "analyst": "analyst"},
    )

    for specialist in ("researcher", "coder", "analyst"):
        graph.add_edge(specialist, "check_escalation")

    graph.add_conditional_edges(
        "check_escalation",
        escalation_dispatch,
        {"release": "release", "pause_for_human": "pause_for_human"},
    )

    graph.add_edge("release", END)
    graph.add_edge("pause_for_human", END)  # resumed manually via the API

    return graph.compile()


compiled_graph = build_graph()
