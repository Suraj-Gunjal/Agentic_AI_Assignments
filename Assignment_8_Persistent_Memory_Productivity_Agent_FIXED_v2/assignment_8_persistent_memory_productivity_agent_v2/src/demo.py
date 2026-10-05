from src.agent import ProductivityMemoryAgent


def main():
    agent = ProductivityMemoryAgent()

    messages = [
        "I prefer studying DSA in the morning.",
        "I am building a flood prediction project.",
        "My goal is to improve Java problem solving.",
        "I prefer simple project documentation.",
        "What project am I building?",
        "What are my study preferences?",
        "What am I trying to improve?",
    ]

    for message in messages:
        result = agent.chat(message)

        print(f"\nUser: {message}")
        print(f"Agent: {result['answer']}")

        if result.get("memory_stored"):
            print("Memory: stored")


if __name__ == "__main__":
    main()
