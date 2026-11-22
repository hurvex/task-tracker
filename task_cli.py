#!/usr/bin/env python3
"""A simple command-line task tracker. Uses only Python's standard library."""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path.cwd() / "tasks.json"
VALID_STATUSES = {"todo", "in-progress", "done"}


def timestamp():
    """Return the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_tasks():
    """Load tasks, creating the JSON file if it does not exist."""
    if not DATA_FILE.exists():
        try:
            DATA_FILE.write_text("[]\n", encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Cannot create {DATA_FILE}: {exc}") from exc

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{DATA_FILE.name} contains invalid JSON. Fix the file and try again "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Cannot read {DATA_FILE}: {exc}") from exc

    if not isinstance(tasks, list):
        raise RuntimeError(f"{DATA_FILE.name} must contain a JSON array.")

    return tasks


def save_tasks(tasks):
    """Save tasks safely using a temporary file and atomic replacement."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            prefix=f"{DATA_FILE.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temp_path = Path(file.name)
            json.dump(tasks, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temp_path, DATA_FILE)
    except OSError as exc:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise RuntimeError(f"Cannot save tasks: {exc}") from exc


def parse_id(value):
    """Validate and convert a task ID."""
    try:
        task_id = int(value)
    except (TypeError, ValueError):
        raise ValueError("Task ID must be a positive whole number.")
    if task_id < 1 or str(task_id) != str(value):
        raise ValueError("Task ID must be a positive whole number.")
    return task_id


def find_task(tasks, task_id):
    for task in tasks:
        if isinstance(task, dict) and task.get("id") == task_id:
            return task
    raise ValueError(f"Task with ID {task_id} was not found.")


def next_id(tasks):
    ids = [
        task["id"]
        for task in tasks
        if isinstance(task, dict)
        and isinstance(task.get("id"), int)
        and not isinstance(task.get("id"), bool)
        and task["id"] > 0
    ]
    return max(ids, default=0) + 1


def require_description(value):
    description = value.strip()
    if not description:
        raise ValueError("Please provide a non-empty task description in quotes.")
    return description


def print_usage():
    print(
        """Task Tracker CLI

Usage:
  python task_cli.py add "Task description"
  python task_cli.py update <id> "New description"
  python task_cli.py delete <id>
  python task_cli.py mark-in-progress <id>
  python task_cli.py mark-done <id>
  python task_cli.py list [all|done|not-done|todo|in-progress]

Examples:
  python task_cli.py add "Buy groceries"
  python task_cli.py update 1 "Buy groceries and milk"
  python task_cli.py mark-in-progress 1
  python task_cli.py list in-progress

Tasks are stored in tasks.json in the current directory."""
    )


def list_tasks(tasks, filter_name="all"):
    allowed_filters = {"all", "done", "not-done", "todo", "in-progress"}
    filter_name = filter_name.lower()

    if filter_name not in allowed_filters:
        raise ValueError(
            "Invalid list filter. Use all, done, not-done, todo, or in-progress."
        )

    def matches(task):
        status = task.get("status") if isinstance(task, dict) else None
        if filter_name == "all":
            return True
        if filter_name == "not-done":
            return status != "done"
        return status == filter_name

    selected = [task for task in tasks if matches(task)]

    if not selected:
        print("No tasks found.")
        return

    print(f"{'ID':<4} {'STATUS':<14} DESCRIPTION")
    print(f"{'--':<4} {'-------------':<14} {'-' * 40}")
    for task in selected:
        if not isinstance(task, dict):
            print(f"{'?':<4} {'invalid':<14} Invalid task entry in JSON")
            continue
        task_id = task.get("id", "?")
        status = task.get("status", "unknown")
        description = task.get("description", "")
        print(f"{str(task_id):<4} {str(status):<14} {description}")


def main(args):
    if not args or args[0] in {"help", "--help", "-h"}:
        print_usage()
        return

    command, *params = args
    tasks = load_tasks()

    if command == "add":
        if len(params) != 1:
            raise ValueError('Usage: python task_cli.py add "Task description"')
        description = require_description(params[0])
        created = timestamp()
        task = {
            "id": next_id(tasks),
            "description": description,
            "status": "todo",
            "createdAt": created,
            "updatedAt": created,
        }
        tasks.append(task)
        save_tasks(tasks)
        print(f"Task added successfully (ID: {task['id']}).")

    elif command == "update":
        if len(params) != 2:
            raise ValueError('Usage: python task_cli.py update <id> "New description"')
        task_id = parse_id(params[0])
        description = require_description(params[1])
        task = find_task(tasks, task_id)
        task["description"] = description
        task["updatedAt"] = timestamp()
        save_tasks(tasks)
        print(f"Task {task_id} updated successfully.")

    elif command == "delete":
        if len(params) != 1:
            raise ValueError("Usage: python task_cli.py delete <id>")
        task_id = parse_id(params[0])
        find_task(tasks, task_id)
        tasks = [task for task in tasks if not (
            isinstance(task, dict) and task.get("id") == task_id
        )]
        save_tasks(tasks)
        print(f"Task {task_id} deleted successfully.")

    elif command in {"mark-in-progress", "mark-done"}:
        if len(params) != 1:
            raise ValueError(f"Usage: python task_cli.py {command} <id>")
        task_id = parse_id(params[0])
        task = find_task(tasks, task_id)
        task["status"] = "done" if command == "mark-done" else "in-progress"
        task["updatedAt"] = timestamp()
        save_tasks(tasks)
        print(f"Task {task_id} marked as {task['status']}.")

    elif command == "list":
        if len(params) > 1:
            raise ValueError(
                "Usage: python task_cli.py list [all|done|not-done|todo|in-progress]"
            )
        list_tasks(tasks, params[0] if params else "all")

    else:
        raise ValueError(
            f"Unknown command: {command}. Run 'python task_cli.py help' for usage."
        )


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(130)
