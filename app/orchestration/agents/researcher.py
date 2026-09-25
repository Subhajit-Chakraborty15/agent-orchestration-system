from app.orchestration.state import AgentState
from app.orchestration.agents.base_agent import call_llm, extract_confidence, strip_confidence_line

SYSTEM_PROMPT = """You are the Researcher agent in a multi-agent system.
Answer factual / "what is" / "explain" / "find information about" questions clearly and concisely.
End your answer with a new line exactly like: CONFIDENCE: 0.0-1.0
Use a lower confidence (below 0.5) if the question needs live/current information you cannot verify."""


def run(state: AgentState) -> AgentState:
    raw = call_llm(SYSTEM_PROMPT, state["user_input"])
    confidence = extract_confidence(raw)
    answer = strip_confidence_line(raw)

    state["agent_output"] = answer
    state["confidence"] = confidence
    return state
