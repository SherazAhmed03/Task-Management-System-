"""
Task Management System
A Python task manager that uses a stack and a queue, with the Claude API
to turn plain-English input into structured tasks.
 
Setup:
    pip install anthropic
    Set your API key:  export ANTHROPIC_API_KEY="your-key"   (Mac/Linux)
                       setx ANTHROPIC_API_KEY "your-key"     (Windows, then reopen the terminal)
Run:
    python task_manager.py
"""
 
import json
import os
import re
from collections import deque
from datetime import datetime
 
import anthropic
 
MODEL = "claude-sonnet-5-5"
PRIORITIES = ["low", "medium", "high", "urgent"]
SAVE_FILE = "tasks.json"
 
 
# ---------- Data structures ----------
 
class Task:
    def __init__(self, name, description="", priority="medium", created=None, completed=False):
        self.name = name
        self.description = description
        self.priority = priority if priority in PRIORITIES else "medium"
        self.completed = completed
        self.created = created or datetime.now()
 
    def __str__(self):
        mark = "x" if self.completed else " "
        return f"[{mark}] {self.name} ({self.priority}) - {self.description}"
 
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "completed": self.completed,
            "created": self.created.isoformat(),
        }
 
    @staticmethod
    def from_dict(d):
        return Task(
            d["name"], d.get("description", ""), d.get("priority", "medium"),
            datetime.fromisoformat(d["created"]), d.get("completed", False),
        )
 
 
class TaskManager:
    def __init__(self):
        self.queue = deque()   # tasks waiting to be done, first in, first out
        self.history = []      # stack of completed tasks, last in, first out
 
    def add(self, task):
        self.queue.append(task)
        self._sort_by_priority()
 
    def _sort_by_priority(self):
        # Highest priority first, then oldest first
        ordered = sorted(self.queue, key=lambda t: (-PRIORITIES.index(t.priority), t.created))
        self.queue = deque(ordered)
 
    def complete_next(self):
        if not self.queue:
            return None
        task = self.queue.popleft()
        task.completed = True
        self.history.append(task)   # push onto the completed stack
        return task
 
    def undo_last(self):
        if not self.history:
            return None
        task = self.history.pop()   # pop the most recent completion
        task.completed = False
        self.add(task)
        return task
 
    def escalate(self, name):
        for task in self.queue:
            if task.name.lower() == name.lower():
                i = PRIORITIES.index(task.priority)
                task.priority = PRIORITIES[min(i + 1, len(PRIORITIES) - 1)]
                self._sort_by_priority()
                return task
        return None
 
    def cleanup(self):
        # Remove duplicate open tasks (same name), keeping the first in line
        seen = set()
        kept = deque()
        for task in self.queue:
            key = task.name.strip().lower()
            if key not in seen:
                seen.add(key)
                kept.append(task)
        removed = len(self.queue) - len(kept)
        self.queue = kept
        return removed
 
    def show(self):
        if not self.queue:
            print("No open tasks.")
        for i, task in enumerate(self.queue, 1):
            print(f"{i}. {task}")
        print(f"Completed: {len(self.history)}")
 
    # ---------- Saving ----------
 
    def save(self, path=SAVE_FILE):
        data = {
            "queue": [t.to_dict() for t in self.queue],
            "history": [t.to_dict() for t in self.history],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
 
    def load(self, path=SAVE_FILE):
        if not os.path.exists(path):
            return
        with open(path) as f:
            data = json.load(f)
        self.queue = deque(Task.from_dict(d) for d in data.get("queue", []))
        self.history = [Task.from_dict(d) for d in data.get("history", [])]
        self._sort_by_priority()
 
 
# ---------- Claude API parsing ----------
 
def extract_json(raw):
    """Find the first {...} block, so code fences or extra text do not break parsing."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise json.JSONDecodeError("no JSON found", raw, 0)
    return json.loads(match.group(0))
 
 
def parse_with_claude(text):
    """Send plain-English text to Claude and get back name, description, priority."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    prompt = (
        "Turn this task into JSON with exactly these keys: "
        '"name" (short title), "description" (one sentence), '
        '"priority" (one of: low, medium, high, urgent, based on how urgent it sounds). '
        "Reply with only the JSON, nothing else.\n\n"
        f"Task: {text}"
    )
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        data = extract_json(response.content[0].text)
        priority = str(data.get("priority", "medium")).lower()
        return Task(data["name"], data.get("description", ""), priority)
    except anthropic.AuthenticationError:
        print("Error 401: the API key is missing or invalid. Check ANTHROPIC_API_KEY.")
    except anthropic.RateLimitError:
        print("Error 429: too many requests. Wait a moment and try again.")
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}")
    except anthropic.APIConnectionError:
        print("Could not reach the API. Check your internet connection.")
    except (json.JSONDecodeError, KeyError):
        print("Claude's reply wasn't valid task JSON. Try rewording the task.")
    return None
 
 
# ---------- Dual-mode CLI ----------
 
def main():
    manager = TaskManager()
    manager.load()
    menu = (
        "\n1. Add task (manual)\n2. Add task (AI, plain English)\n3. Show tasks\n"
        "4. Complete next task\n5. Undo last completion\n6. Escalate a task\n"
        "7. Clean up queue\n8. Quit"
    )
    while True:
        print(menu)
        choice = input("Choose: ").strip()
 
        if choice == "1":
            name = input("Name: ").strip()
            if not name:
                print("Name is required.")
                continue
            desc = input("Description: ").strip()
            prio = input(f"Priority {PRIORITIES}: ").strip().lower()
            manager.add(Task(name, desc, prio))
            print("Task added.")
 
        elif choice == "2":
            if not os.environ.get("ANTHROPIC_API_KEY"):
                print("Set ANTHROPIC_API_KEY first to use AI mode.")
                continue
            text = input("Describe the task: ").strip()
            task = parse_with_claude(text)
            if task:
                manager.add(task)
                print(f"Added: {task}")
 
        elif choice == "3":
            manager.show()
 
        elif choice == "4":
            task = manager.complete_next()
            print(f"Completed: {task.name}" if task else "Nothing to complete.")
 
        elif choice == "5":
            task = manager.undo_last()
            print(f"Moved back to queue: {task.name}" if task else "Nothing to undo.")
 
        elif choice == "6":
            name = input("Task name to escalate: ").strip()
            task = manager.escalate(name)
            print(f"Now {task.priority}: {task.name}" if task else "Task not found.")
 
        elif choice == "7":
            print(f"Removed {manager.cleanup()} duplicate task(s).")
 
        elif choice == "8":
            break
 
        else:
            print("Pick a number from 1 to 8.")
            continue
 
        manager.save()
 
    manager.save()
 
 
if __name__ == "__main__":
    main()
 