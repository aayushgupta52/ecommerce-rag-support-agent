import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("logs.jsonl")


def log_interaction(
    session_id: str,
    user_message: str,
    retrieved_chunks: list[dict] | None = None,
    tool_calls: list[dict] | None = None,
    final_response: str = "",
    handoff: bool = False,
    error: str | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_message": user_message,
        "retrieved_chunks": retrieved_chunks or [],
        "tool_calls": tool_calls or [],
        "final_response": final_response,
        "handoff": handoff,
        "error": error,
    }

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        