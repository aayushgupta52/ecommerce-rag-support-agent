from app.agent import Agent
import uuid


def main():
    print("=" * 60)
    print("Aster & Row Support Agent (CLI)")
    print("Type your message, or 'exit' to quit.")
    print("=" * 60)

    agent = Agent()
    session_id = str(uuid.uuid4())

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        reply = agent.handle_message(session_id, user_input)
        print(f"\nAgent: {reply}")


if __name__ == "__main__":
    main()