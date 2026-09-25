from fastapi import FastAPI
from pydantic import BaseModel
from app.memory import postgres_store
from app.queue.tasks import run_agent_turn

app = FastAPI(title="Agent Orchestration System")


@app.on_event("startup")
def startup():
    postgres_store.init_db()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ApprovalRequest(BaseModel):
    approved: bool
    edited_answer: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):
    """Kicks off an async agent run via Celery and returns the task id."""
    task = run_agent_turn.delay(req.session_id, req.message)
    return {"task_id": task.id}


@app.get("/chat/{task_id}")
def chat_result(task_id: str):
    task = run_agent_turn.AsyncResult(task_id)
    if not task.ready():
        return {"status": "pending"}
    return {"status": "done", "result": task.result}


@app.get("/approvals")
def list_pending_approvals():
    return postgres_store.get_pending_approvals()


@app.post("/approvals/{turn_id}/resolve")
def resolve_approval(turn_id: int, req: ApprovalRequest):
    postgres_store.resolve_approval(turn_id, req.approved)
    return {"status": "resolved", "turn_id": turn_id, "approved": req.approved}


@app.get("/history/{session_id}")
def history(session_id: str):
    return postgres_store.get_history(session_id)


@app.get("/health")
def health():
    return {"status": "ok"}
