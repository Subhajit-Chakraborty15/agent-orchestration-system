from typing import TypedDict, List, Optional, Literal

AgentName = Literal["researcher", "coder", "analyst"]


class AgentState(TypedDict, total=False):
    session_id: str
    user_input: str
    history: List[dict]          # [{"role": "user"/"agent", "content": str}]
    route: Optional[AgentName]   # which specialist the supervisor picked
    agent_output: Optional[str]
    confidence: Optional[float]  # 0..1, set by the specialist agent
    needs_approval: bool         # set True to trigger human-in-the-loop pause
    approved: Optional[bool]     # set by the human via the API/UI
    final_answer: Optional[str]
