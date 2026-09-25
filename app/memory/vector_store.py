import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

_client = chromadb.HttpClient(
    host=settings.CHROMA_HOST,
    port=settings.CHROMA_PORT,
    settings=ChromaSettings(anonymized_telemetry=False),
)

# Uses ChromaDB's bundled default embedding function (all-MiniLM-L6-v2, runs
# locally via onnxruntime) -- no external embedding API, fully free.
_collection = _client.get_or_create_collection(name="agent_memory")


def remember(session_id: str, text: str, metadata: dict | None = None):
    doc_id = f"{session_id}-{_collection.count()}"
    _collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[{"session_id": session_id, **(metadata or {})}],
    )


def recall(session_id: str, query: str, k: int = 4) -> list[str]:
    """Semantic search over everything remembered for this session."""
    results = _collection.query(
        query_texts=[query],
        n_results=k,
        where={"session_id": session_id},
    )
    documents = results.get("documents", [[]])
    return documents[0] if documents else []
