import re
import ollama
from app.config import settings

_client = ollama.Client(host=settings.OLLAMA_HOST)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Single free, local LLM call via Ollama. No API keys, no cost."""
    response = _client.chat(
        model=settings.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"].strip()


def extract_confidence(text: str, default: float = 0.75) -> float:
    """
    Agents are asked to end their reply with a line like:
    CONFIDENCE: 0.8
    This pulls that number out; falls back to `default` if missing/unparseable.
    """
    match = re.search(r"CONFIDENCE:\s*([0-9]*\.?[0-9]+)", text)
    if not match:
        return default
    try:
        value = float(match.group(1))
        return max(0.0, min(1.0, value))
    except ValueError:
        return default


def strip_confidence_line(text: str) -> str:
    return re.sub(r"\n?CONFIDENCE:\s*[0-9]*\.?[0-9]+\s*$", "", text).strip()
