import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/todos.json")

class TodoState:
    def __init__(self):
        self.todos = []
        self.next_id = 1
        self.load()

    def load(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self.todos = data.get("todos", [])
                self.next_id = data.get("next_id", 1)
            except (json.JSONDecodeError, OSError):
                self.todos = []
                self.next_id = 1
        else:
            self.save()

    def save(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(
            json.dumps(
                {"todos": self.todos, "next_id": self.next_id},
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    def add(self, title, priority="medium"):
        todo = {
            "id": self.next_id,
            "title": title.strip(),
            "priority": priority.lower(),
            "completed": False,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
        self.todos.append(todo)
        self.next_id += 1
        self.save()
        return todo

    def list_all(self, status="all"):
        if status == "pending":
            return [t for t in self.todos if not t["completed"]]
        if status == "completed":
            return [t for t in self.todos if t["completed"]]
        return list(self.todos)

    def complete(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                self.save()
                return todo
        return None

    def delete(self, todo_id):
        for index, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                removed = self.todos.pop(index)
                self.save()
                return removed
        return None

    def search(self, query):
        q = query.lower().strip()
        return [t for t in self.todos if q in t["title"].lower()]

    def clear_completed(self):
        before = len(self.todos)
        self.todos = [t for t in self.todos if not t["completed"]]
        removed = before - len(self.todos)
        self.save()
        return removed

    def summary(self):
        total = len(self.todos)
        completed = sum(t["completed"] for t in self.todos)
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed
        }
