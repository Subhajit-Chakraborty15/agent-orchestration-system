from app.orchestration.state import AgentState
from app.orchestration.agents.base_agent import call_llm, extract_confidence, strip_confidence_line

SYSTEM_PROMPT = """You are the Analyst agent in a multi-agent system.
Handle requests to compare options, weigh trade-offs, summarize data, or make a recommendation/decision.
End your answer with a new line exactly like: CONFIDENCE: 0.0-1.0
Use a lower confidence (below 0.5) whenever the request asks you to make a decision with real-world
consequences (financial, legal, hiring, safety) -- that should be escalated to a human."""


def run(state: AgentState) -> AgentState:
    raw = call_llm(SYSTEM_PROMPT, state["user_input"])
    confidence = extract_confidence(raw)
    answer = strip_confidence_line(raw)

    state["agent_output"] = answer
    state["confidence"] = confidence
    return state
