# TodoPilot — Agentic AI To-Do Manager

A command-line to-do manager built for an Agentic AI assignment.

## Features

- Ollama LLM integration
- Agentic tool calling
- Persistent JSON state
- Add, list, search, complete and delete tasks
- Clear completed tasks
- Task priorities
- Dashboard with completion progress
- Rich terminal UI
- Natural-language commands
- No cloud API key required

## Architecture

User → Rich CLI → TodoPilot Agent → Ollama LLM → Tools → TodoState → data/todos.json

The LLM decides which tool to call based on the user's natural-language request. The tools perform the actual state changes.

## Requirements

- Python 3.10+
- Ollama installed and running
- A tool-capable Ollama model

## Setup

### 1. Install Ollama

Install Ollama from its official website and make sure the Ollama service is running.

### 2. Pull a model

```bash
ollama pull qwen2.5:3b
```

You can use another tool-capable model by setting `OLLAMA_MODEL`.

### 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
python main.py
```

## Example interaction

```text
You: Add a high priority task to finish my Agentic AI assignment

TodoPilot:
Added task "finish my Agentic AI assignment" with high priority.

You: Show my pending tasks

TodoPilot:
Your pending tasks are...

You: Mark the Agentic AI assignment as complete

TodoPilot:
Task 1 has been marked as completed.
```

## Assignment concepts demonstrated

1. Agent perception: receives natural-language user input.
2. Reasoning: Ollama LLM interprets the intent.
3. Action selection: LLM selects an appropriate tool.
4. Environment/state: tasks are stored in JSON.
5. Tool execution: Python functions modify the state.
6. Feedback: tool results are returned to the LLM.
7. Persistent memory: state survives program restarts.
8. Human interaction: Rich CLI provides a visual interface.

## Suggested viva explanation

"This project demonstrates a simple agentic architecture. The user does not have to remember command syntax. They can use natural language. The Ollama LLM acts as the decision-making component and selects tools such as add_todo, list_todos, complete_todo, delete_todo, search_todos and get_summary. The tools operate on a persistent JSON state. The Rich library provides the terminal UI, dashboard, tables and progress indicator."

## Project structure

```text
todo_agent_ollama/
├── app/
│   ├── agent.py
│   ├── state.py
│   ├── tools.py
│   └── ui.py
├── data/
│   └── todos.json
├── .env.example
├── main.py
├── requirements.txt
└── README.md
```
