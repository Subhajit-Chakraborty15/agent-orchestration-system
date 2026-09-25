from app.queue.celery_app import celery_app
from app.orchestration.graph import compiled_graph
from app.memory import postgres_store, vector_store


@celery_app.task(name="run_agent_turn")
def run_agent_turn(session_id: str, user_input: str) -> dict:
    postgres_store.ensure_session(session_id)
    postgres_store.save_turn(session_id, role="user", content=user_input)

    initial_state = {
        "session_id": session_id,
        "user_input": user_input,
        "history": postgres_store.get_history(session_id),
        "needs_approval": False,
    }

    result_state = compiled_graph.invoke(initial_state)

    postgres_store.save_turn(
        session_id,
        role="agent",
        content=result_state.get("agent_output", ""),
        route=result_state.get("route"),
        needs_approval=result_state.get("needs_approval", False),
        approved=result_state.get("approved"),
    )

    # store in semantic memory so future turns in this session can recall it
    vector_store.remember(session_id, f"User: {user_input}\nAgent: {result_state.get('agent_output', '')}")

    return result_state
