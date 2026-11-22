# Task Tracker CLI (Python)

A command-line task tracker built with Python's standard library only. It stores
tasks in `tasks.json` in the current working directory and creates that file
automatically when it does not exist.

## Requirements

- Python 3.8 or newer
- No external libraries or frameworks

## Run

Open a terminal in the folder containing `task_cli.py` and run:

```bash
python task_cli.py help
python task_cli.py add "Buy groceries"
python task_cli.py add "Finish homework"
python task_cli.py list
python task_cli.py update 1 "Buy groceries and milk"
python task_cli.py mark-in-progress 2
python task_cli.py mark-done 1
python task_cli.py list done
python task_cli.py list not-done
python task_cli.py list in-progress
python task_cli.py delete 2
```

On some systems, use `python3` instead of `python`.

## Commands

| Command | Purpose |
|---|---|
| `add "description"` | Add a task (initial status: `todo`) |
| `update <id> "description"` | Update a task description |
| `delete <id>` | Delete a task |
| `mark-in-progress <id>` | Mark a task as in progress |
| `mark-done <id>` | Mark a task as done |
| `list` or `list all` | List all tasks |
| `list done` | List completed tasks |
| `list not-done` | List tasks not completed |
| `list todo` | List tasks not yet started |
| `list in-progress` | List tasks in progress |

Put descriptions containing spaces inside quotation marks. Task IDs are
assigned automatically. Each task stores its ID, description, status, creation
timestamp, and last-updated timestamp.

## Error handling

The program validates command arguments, task IDs, descriptions, and list
filters. It reports missing task IDs and handles unreadable or invalid JSON
files with clear error messages. File updates use a temporary file followed
by replacement to reduce the chance of a partially written JSON file.
## Project URL
https://roadmap.sh/projects/task-tracker
