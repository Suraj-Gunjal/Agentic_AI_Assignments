from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from app.agent import TodoAgent
from app.ui import show_header, show_dashboard, show_tasks, show_help, show_result

console = Console()

def main():
    show_header()
    show_dashboard()
    console.print("[dim]Type /help for commands. Or just tell the agent what you need.[/dim]\n")

    try:
        agent = TodoAgent()
    except Exception as exc:
        console.print(f"[bold red]Could not initialize Ollama:[/bold red] {exc}")
        return

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in {"/exit", "/quit"}:
            console.print("[bold cyan]Goodbye! Your tasks are saved.[/bold cyan]")
            break
        if command == "/help":
            show_help()
            continue
        if command == "/all":
            show_tasks("all")
            continue
        if command == "/pending":
            show_tasks("pending")
            continue
        if command == "/done":
            show_tasks("completed")
            continue
        if command == "/dashboard":
            show_dashboard()
            continue

        with console.status("[bold cyan]TodoPilot is thinking and using tools...[/bold cyan]"):
            try:
                result = agent.ask(user_input)
            except Exception as exc:
                result = f"Error: {exc}"

        show_result(result)
        show_dashboard()

if __name__ == "__main__":
    main()
