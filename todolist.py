from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import pyfiglet

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView

logging.basicConfig(
    filename="todo_errors.log",
    level=logging.ERROR,
    format="%(asctime)s  %(levelname)s  %(message)s",
)

INTRO_LINES = [
    "  WELCOME TO YOUR TERMINAL TODO LIST  ",
    "─────────────────────────────────────────",
    "⌨   Tab          Jump between input and list",
    "⌨   Arrow Keys   Navigate tasks up and down",
    "⌨   Spacebar     Toggle task complete / pending",
    "⌨   D            Delete the focused task",
    "⌨   Q            Save and quit",
    "─────────────────────────────────────────",
    "  Type a task above and press Enter to begin",
]


class TodoItem(ListItem):
    """Single task row — owns its text, completion state, and layout."""

    def __init__(self, task_text: str, completed: bool = False) -> None:
        super().__init__()
        self.task_text = task_text
        self.is_completed = completed

    def compose(self) -> ComposeResult:
        status = "[✓]" if self.is_completed else "[ ]"
        with Horizontal(classes="task-item-row"):
            yield Label(status, classes="status-box")
            yield Label(self.task_text, classes="task-text")

    def on_mount(self) -> None:
        # Apply the done styling class immediately for tasks loaded as completed
        if self.is_completed:
            self.add_class("item-done")


class TodoApp(App):
    """
    Keyboard-first terminal todo manager built on Textual.

    Every mutation (add, toggle, delete) is flushed to disk immediately
    so you never lose work to an unexpected exit. Tasks survive restarts,
    crashes, and closed terminals — no cloud, no account, no nonsense.
    """

    CSS_PATH = "todo.css"
    DB_FILE = Path("tasks.json")

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("tab", "focus_next", "Shift Focus"),
        ("space", "toggle_item", "Toggle Done"),
        ("d", "delete_item", "Delete Task"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="app-container"):
                ascii_title = pyfiglet.figlet_format("To-Do List", font="slant")
                yield Label(ascii_title, id="title-text")

                with Horizontal(id="input-container"):
                    yield Input(
                        placeholder="Type a task and press Enter…",
                        id="task-input",
                    )
                    yield Button("Add  [Enter]", variant="primary", id="add-btn")

                yield ListView(id="task-list")

        yield Footer()

    def on_mount(self) -> None:
        self.load_tasks()

    # ── Persistence ────────────────────────────────────────────────────────────

    def load_tasks(self) -> None:
        """Read tasks.json and hydrate the list. Shows intro guide if empty."""
        if not self.DB_FILE.exists():
            self._refresh_intro()
            return

        try:
            raw = self.DB_FILE.read_text(encoding="utf-8")
            tasks: list[dict] = json.loads(raw)
            task_list = self.query_one("#task-list", ListView)

            for entry in tasks:
                task_list.append(
                    TodoItem(entry["text"], completed=entry.get("completed", False))
                )

        except (json.JSONDecodeError, KeyError, OSError) as exc:
            logging.error("Failed to load %s: %s", self.DB_FILE, exc)

        self._refresh_intro()

    def save_tasks(self) -> None:
        """Serialize current task state to disk. Logs on failure, never raises."""
        task_list = self.query_one("#task-list", ListView)
        payload = [
            {"text": item.task_text, "completed": item.is_completed}
            for item in task_list.children
            if isinstance(item, TodoItem)
        ]
        try:
            self.DB_FILE.write_text(json.dumps(payload, indent=4), encoding="utf-8")
        except OSError as exc:
            logging.error("Could not write %s: %s", self.DB_FILE, exc)

    # ── List helpers ────────────────────────────────────────────────────────────

    def _refresh_intro(self) -> None:
        """
        Shows the onboarding guide when no real tasks exist.
        Removes it the moment a TodoItem is present.
        """
        task_list = self.query_one("#task-list", ListView)

        for child in list(task_list.children):
            if child.has_class("intro-item"):
                child.remove()

        has_tasks = any(isinstance(c, TodoItem) for c in task_list.children)
        if not has_tasks:
            for line in INTRO_LINES:
                row = ListItem(Label(line))
                row.add_class("intro-item")
                task_list.append(row)

    # ── Task mutations ──────────────────────────────────────────────────────────

    def _add_task(self) -> None:
        """Pull text from the input field, append a TodoItem, and save."""
        input_widget = self.query_one("#task-input", Input)
        text = input_widget.value.strip()
        if not text:
            return

        task_list = self.query_one("#task-list", ListView)

        # Clear the intro guide before the first real task lands
        if any(c.has_class("intro-item") for c in task_list.children):
            task_list.clear()

        task_list.append(TodoItem(text))
        input_widget.value = ""
        input_widget.focus()
        self.save_tasks()

    def _toggle_task(self, item: TodoItem) -> None:
        """Flip a task's completion state and sync to disk."""
        item.is_completed = not item.is_completed
        status_label = item.query_one(".status-box", Label)

        if item.is_completed:
            item.add_class("item-done")
            status_label.update("[✓]")
        else:
            item.remove_class("item-done")
            status_label.update("[ ]")

        self.save_tasks()

    # ── Event handlers ──────────────────────────────────────────────────────────

    @on(Button.Pressed, "#add-btn")
    def on_add_button(self) -> None:
        self._add_task()

    @on(Input.Submitted, "#task-input")
    def on_input_submitted(self) -> None:
        self._add_task()

    @on(ListView.Selected, "#task-list")
    def on_row_selected(self, event: ListView.Selected) -> None:
        """Enter on a focused row toggles its completion state."""
        if isinstance(event.item, TodoItem):
            self._toggle_task(event.item)

    # ── Keybind actions ─────────────────────────────────────────────────────────

    def action_toggle_item(self) -> None:
        """Spacebar: toggle the highlighted task."""
        task_list = self.query_one("#task-list", ListView)
        if task_list.has_focus and task_list.index is not None:
            active = task_list.children[task_list.index]
            if isinstance(active, TodoItem):
                self._toggle_task(active)

    def action_delete_item(self) -> None:
        """D key: remove the highlighted task and keep the cursor position sane."""
        task_list = self.query_one("#task-list", ListView)
        if not (task_list.has_focus and task_list.index is not None):
            return

        current_index = task_list.index
        active = task_list.children[current_index]

        if not isinstance(active, TodoItem):
            return

        active.remove()
        self.save_tasks()

        remaining = list(task_list.children)
        if remaining:
            task_list.index = min(current_index, len(remaining) - 1)

        self._refresh_intro()

    def action_quit(self) -> None:
        """Q key: explicit save-then-exit so nothing slips through."""
        self.save_tasks()
        self.exit()


if __name__ == "__main__":
    TodoApp().run()
