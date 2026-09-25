from app.orchestration.state import AgentState
from app.orchestration.agents.base_agent import call_llm

ROUTER_PROMPT = """You are a routing supervisor for a multi-agent system.
Read the user's message and decide which ONE specialist should handle it.

Specialists:
- researcher: factual questions, explanations, "what is / how does X work"
- coder: ANY request to write, generate, review, debug, or explain a script, function, or program,
  including scripts that perform file operations, delete data, or automate system tasks
- analyst: comparisons, trade-offs, recommendations, or decisions -- NOT code-writing requests

Reply with exactly one word: researcher, coder, or analyst. Nothing else."""
VALID_ROUTES = {"researcher", "coder", "analyst"}


def route(state: AgentState) -> AgentState:
    """Supervisor node: decides which specialist agent handles this turn."""
    decision = call_llm(ROUTER_PROMPT, state["user_input"]).strip().lower()

    # fallback keyword routing if the LLM returns something unexpected
    if decision not in VALID_ROUTES:
        text = state["user_input"].lower()
        if any(k in text for k in ["code", "bug", "function", "script", "debug"]):
            decision = "coder"
        elif any(k in text for k in ["compare", "should i", "recommend", "trade-off", "decide"]):
            decision = "analyst"
        else:
            decision = "researcher"

    state["route"] = decision  # type: ignore[assignment]
    return state
