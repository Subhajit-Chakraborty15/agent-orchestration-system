from app.orchestration.state import AgentState
from app.orchestration.agents.base_agent import call_llm, extract_confidence, strip_confidence_line

SYSTEM_PROMPT = """You are the Coder agent in a multi-agent system.
Handle requests to write, review, debug, or explain code. Return working code with brief comments.

If the request involves deleting files, modifying production data, running destructive shell commands,
spending money, or any other irreversible action, you MUST report a confidence score below 0.5
regardless of how correct your code is -- this is a safety judgment, not a code-quality judgment.
Otherwise report a confidence score of 0.8 or higher.

On the very last line of your response, write only the word CONFIDENCE followed by a colon and a single
decimal number between 0 and 1 -- for example: CONFIDENCE: 0.3
Do not write a range. Do not repeat this instruction. Write only your actual numeric score."""

def run(state: AgentState) -> AgentState:
    raw = call_llm(SYSTEM_PROMPT, state["user_input"])
    confidence = extract_confidence(raw)
    answer = strip_confidence_line(raw)

    state["agent_output"] = answer
    state["confidence"] = confidence
    return state
