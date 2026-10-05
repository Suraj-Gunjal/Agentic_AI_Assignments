from app.state import TodoState

state = TodoState()


def add_todo(title: str, priority: str = "medium") -> dict:
    """Add a new task."""
    priority = priority.lower()

    if priority not in {"low", "medium", "high"}:
        priority = "medium"

    return state.add(title, priority)


def list_todos(status: str = "all") -> list:
    """List tasks."""
    if status not in {"all", "pending", "completed"}:
        status = "all"

    return state.list_all(status)


def complete_todo(todo_id: int) -> dict:
    """Mark a task as completed."""
    todo = state.complete(todo_id)

    if todo:
        return todo

    return {
        "error": f"Task {todo_id} was not found."
    }


def delete_todo(todo_id: int) -> dict:
    """Delete a task."""
    todo = state.delete(todo_id)

    if todo:
        return todo

    return {
        "error": f"Task {todo_id} was not found."
    }


def search_todos(query: str) -> list:
    """Search tasks."""
    return state.search(query)


def clear_completed() -> dict:
    """Delete all completed tasks."""
    removed = state.clear_completed()

    return {
        "removed": removed
    }


def get_summary() -> dict:
    """Get task statistics."""
    return state.summary()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "Add a new task to the todo list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title."
                    },
                    "priority": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high"
                        ],
                        "description": "Task priority."
                    }
                },
                "required": [
                    "title"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "List todo tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "all",
                            "pending",
                            "completed"
                        ],
                        "description": "Which tasks to show."
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": "Mark a todo task as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "The numeric ID of the task."
                    }
                },
                "required": [
                    "todo_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "Delete a todo task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "The numeric ID of the task."
                    }
                },
                "required": [
                    "todo_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_todos",
            "description": "Search the todo list by task title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text."
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "clear_completed",
            "description": "Delete all completed tasks.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get total, pending and completed task counts.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


FUNCTIONS = {
    "add_todo": add_todo,
    "list_todos": list_todos,
    "complete_todo": complete_todo,
    "delete_todo": delete_todo,
    "search_todos": search_todos,
    "clear_completed": clear_completed,
    "get_summary": get_summary
}