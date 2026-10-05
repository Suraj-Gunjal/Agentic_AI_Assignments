from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from app.tools import state

console = Console()

def show_header():
    title = Text("TODO PILOT", style="bold cyan")
    subtitle = Text("Agentic AI • Ollama • Persistent State", style="dim")
    console.print(Panel(
        Align.center(Text.assemble(title, "\n", subtitle)),
        border_style="cyan",
        padding=(1, 2)
    ))

def show_dashboard():
    data = state.summary()
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Total", str(data["total"]))
    table.add_row("Pending", str(data["pending"]))
    table.add_row("Completed", str(data["completed"]))

    progress_value = 0 if data["total"] == 0 else int(data["completed"] * 100 / data["total"])
    progress = Progress(
        TextColumn("[bold]Progress[/bold]"),
        BarColumn(),
        TextColumn(f"{progress_value}%")
    )
    progress.add_task("done", total=100, completed=progress_value)

    console.print(Panel(table, title="Dashboard", border_style="blue"))
    console.print(progress)
    console.print()

def show_tasks(status="all"):
    tasks = state.list_all(status)
    table = Table(title=f"{status.title()} Tasks", expand=True)
    table.add_column("ID", justify="center", width=5)
    table.add_column("Task", ratio=1)
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")

    for todo in tasks:
        priority = todo["priority"].upper()
        priority_style = {
            "HIGH": "bold red",
            "MEDIUM": "yellow",
            "LOW": "green"
        }.get(priority, "white")
        status_text = "DONE" if todo["completed"] else "PENDING"
        status_style = "green" if todo["completed"] else "cyan"
        title = f"[dim strike]{todo['title']}[/dim strike]" if todo["completed"] else todo["title"]

        table.add_row(
            str(todo["id"]),
            title,
            f"[{priority_style}]{priority}[/{priority_style}]",
            f"[{status_style}]{status_text}[/{status_style}]"
        )

    console.print(table)

def show_help():
    help_text = """
[bold cyan]Natural language examples[/bold cyan]

  Add a task to study DSA with high priority
  Show my pending tasks
  Mark task 3 as complete
  Delete the task about buying a guitar
  Search for tasks containing project
  Give me a summary
  Clear all completed tasks

[bold cyan]Commands[/bold cyan]

  /all       Show all tasks
  /pending   Show pending tasks
  /done      Show completed tasks
  /dashboard Show dashboard
  /help      Show help
  /exit      Exit Todo Pilot
"""
    console.print(Panel(help_text, title="Help", border_style="magenta"))

def show_result(message):
    console.print(Panel(message, title="TodoPilot", border_style="green"))
