from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, list[Message]] = {}

    def get_history(self, session_id: str) -> list[Message]:
        return self._sessions.setdefault(session_id, [])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        history = self.get_history(session_id)
        history.append(Message(role=role, content=content))

    def to_llm_format(self, session_id: str) -> list[dict]:
        history = self.get_history(session_id)
        return [{"role": m.role, "content": m.content} for m in history]

if __name__ == "__main__":
    store = SessionStore()

    session_id = "test-session-1"
    store.add_message(session_id, "user", "Do you ship internationally?")
    store.add_message(session_id, "assistant", "Yes, we ship to Canada.")
    store.add_message(session_id, "user", "What about delivery time?")

    print("History for session-1:")
    for msg in store.to_llm_format(session_id):
        print(f"  {msg['role']}: {msg['content']}")

    other_session = "test-session-2"
    store.add_message(other_session, "user", "Where is my order ORD-1001?")

    print("\nHistory for session-2 (should be separate):")
    for msg in store.to_llm_format(other_session):
        print(f"  {msg['role']}: {msg['content']}")

    print(f"\nTotal sessions tracked: {len(store._sessions)}")