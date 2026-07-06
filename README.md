---
update: <img width="1326" height="956" alt="PHOTO-2026-07-02-18-01-16" src="https://github.com/user-attachments/assets/13a2f7ef-c307-46c5-8dfd-5761215accac" />
https://hackathon.blackpandalabs.in/build-sprint-2026-results

---
# midnight-blackpanda-hackthon
creating a hackathon project that is open  source. the idea is a to-do list cli with additional capability. its python project. its a full cli with mouse controls.

# todo-tui

A terminal-based task manager that solves a problem every developer quietly
lives with: your tools are scattered across browser tabs, native apps, and
sticky note widgets, but your actual work happens in the terminal. Every time
you leave it to write down a thought, you pay a context-switching tax that
compounds across a full workday.

todo-tui puts your task list inside the same environment where you already
work. No alt-tab. No mouse. No browser. You open a split pane, write the
thought down in under two seconds, and you're back in the code.

---

## The real cost of context switching

Research from the University of California Irvine puts the average recovery
time after an interruption at over 23 minutes. For developers working in the
terminal, switching to a GUI app to jot down a single task is exactly that
kind of interruption — small in isolation, catastrophic at scale.

Across a 5-day workweek with even three of these switches per day, you're
bleeding over an hour of deep work every week. todo-tui doesn't eliminate
interruptions, but it removes the environment switch entirely. The terminal
stays the terminal.

---

## Features

- Keyboard-only interface — mouse events are not handled by design
- Instant task persistence — every change writes to disk immediately,
  no explicit save step required
- Crash-safe — tasks survive unexpected exits, killed terminals, and
  power loss (within OS write buffer limits)
- Zero external accounts — your data is a local JSON file that you own
- Graceful error recovery — corrupt or missing task file starts fresh
  and logs the error rather than crashing
- Onboarding guide that disappears the moment your first real task lands

---

## Installation

Python 3.10 or higher is required.

```bash
pip install textual pyfiglet
```

Clone the repo and launch:

```bash
python todolist.py
```

---

## Keybindings

| Key         | Action                           |
|-------------|----------------------------------|
| Enter       | Add task (when input is focused) |
| Tab         | Switch focus — input ↔ list      |
| ↑ / ↓       | Navigate tasks                   |
| Space       | Toggle task complete / pending   |
| D           | Delete focused task              |
| Q           | Save and quit                    |

---

## How data persistence works

Every add, toggle, and delete immediately rewrites `tasks.json` in the
working directory. There is no manual save. If the process is killed between
two actions, you lose at most the last action taken — and even then only if
the OS hadn't flushed the write yet, which on modern filesystems is rare.

On startup the app reads the file and restores your list exactly as you left
it. If the file is malformed or missing, the app starts with a clean slate
and appends a timestamped error to `todo_errors.log`.

Recommended additions to your `.gitignore`:
tasks.json

todo_errors.log

---

## Project structure
.

├── todolist.py       application logic and widget definitions

├── todo.css          Textual CSS layout and theme tokens

├── tasks.json        auto-generated on first task add

└── todo_errors.log   auto-generated on load or save failure

---

## Why not a plain text file?

`echo "fix the auth bug" >> todo.txt` is genuinely unbeatable for raw speed.
But a flat file gives you no way to mark something done without deleting it,
no keyboard navigation, no visual separation between pending and complete
work. todo-tui gives you all of that while staying just as close to the metal
— still a single Python file, still zero network access, still no account.

---

## Dependencies

- [Textual](https://github.com/Textualize/textual) — Python TUI framework
- [pyfiglet](https://github.com/pwaller/pyfiglet) — ASCII art title rendering

Both are pure Python and install without any system-level dependencies.

---

## Contributing

Issues and pull requests are welcome. The core application is under 200 lines
of Python — getting oriented takes about five minutes. If you're adding a
feature, open an issue first so we can agree on scope before you write the
code.
