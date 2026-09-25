from app.orchestration.state import AgentState
from app.config import settings


RISKY_KEYWORDS = [
    "delete", "remove", "rm -rf", "drop table", "truncate",
    "format", "shutil.rmtree", "os.remove", "sudo", "chmod 777",
]


def _mentions_risky_action(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in RISKY_KEYWORDS)


def check(state: AgentState) -> AgentState:
    """
    Decides whether this turn needs a human to approve before the answer
    is released to the user. Triggered either by the specialist agent's
    own low confidence score, or by a deterministic keyword check as a
    safety net for actions the model doesn't reliably flag itself.
    """
    confidence = state.get("confidence", 1.0) or 1.0
    low_confidence = confidence < settings.CONFIDENCE_THRESHOLD
    risky = _mentions_risky_action(state.get("user_input", "")) or \
            _mentions_risky_action(state.get("agent_output", ""))

    state["needs_approval"] = low_confidence or risky
    if not state["needs_approval"]:
        state["approved"] = True
    return state


def apply_human_decision(state: AgentState, approved: bool, edited_answer: str | None = None) -> AgentState:
    """Called from the API when a human resolves a pending escalation."""
    state["approved"] = approved
    if approved:
        state["final_answer"] = edited_answer or state.get("agent_output")
    else:
        state["final_answer"] = "Rejected by reviewer. No answer released."
    return state
