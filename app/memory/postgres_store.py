from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.POSTGRES_DSN, pool_pre_ping=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS turns (
    id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES sessions(session_id),
    role TEXT NOT NULL,              -- 'user' or 'agent'
    content TEXT NOT NULL,
    route TEXT,                      -- which specialist handled it
    needs_approval BOOLEAN DEFAULT FALSE,
    approved BOOLEAN,
    created_at TIMESTAMP DEFAULT now()
);
"""


def init_db():
    with engine.begin() as conn:
        conn.execute(text(SCHEMA))


def ensure_session(session_id: str):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO sessions (session_id) VALUES (:sid) ON CONFLICT DO NOTHING"),
            {"sid": session_id},
        )


def save_turn(session_id: str, role: str, content: str, route: str | None = None,
              needs_approval: bool = False, approved: bool | None = None):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO turns (session_id, role, content, route, needs_approval, approved)
                VALUES (:sid, :role, :content, :route, :needs_approval, :approved)
            """),
            {
                "sid": session_id, "role": role, "content": content,
                "route": route, "needs_approval": needs_approval, "approved": approved,
            },
        )


def get_history(session_id: str, limit: int = 20):
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT role, content, route, needs_approval, approved, created_at
                FROM turns WHERE session_id = :sid
                ORDER BY created_at ASC LIMIT :limit
            """),
            {"sid": session_id, "limit": limit},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_pending_approvals():
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT id, session_id, content, route, created_at
                FROM turns WHERE needs_approval = TRUE AND approved IS NULL
                ORDER BY created_at ASC
            """)
        ).mappings().all()
    return [dict(r) for r in rows]


def resolve_approval(turn_id: int, approved: bool):
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE turns SET approved = :approved WHERE id = :id"),
            {"approved": approved, "id": turn_id},
        )
