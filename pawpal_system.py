"""PawPal+ logic layer (backend classes).

Phase 4: adds smarter scheduling — sorting by time, filtering, recurring
tasks, and lightweight conflict detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

# Priority labels ranked so higher numbers schedule first.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# How many days forward each recurrence frequency repeats.
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""

    name: str
    duration_min: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "daily"  # "daily" | "weekly" | "once"
    time: str = ""  # scheduled start time in "HH:MM" (24h), optional
    due_date: date | None = None
    done: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def priority_value(self) -> int:
        """Return the numeric rank of this task's priority (higher = sooner)."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, not-done copy due next cycle, or None if non-recurring."""
        step = FREQUENCY_DAYS.get(self.frequency.lower())
        if step is None:
            return None
        base = self.due_date or date.today()
        return replace(self, due_date=base + timedelta(days=step), done=False)


@dataclass
class Pet:
    """A pet owned by the user, with its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """The pet owner, including their daily time budget and preferences."""

    name: str
    minutes_available: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def list_pets(self) -> list[Pet]:
        """Return all pets owned by this user."""
        return self.pets

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of the owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily plan and runs smarter scheduling logic for an owner."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self._last_skipped: list[tuple[Pet, Task]] = []

    # --- sorting -----------------------------------------------------------
    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted by their "HH:MM" time; untimed tasks go last."""
        if tasks is None:
            tasks = [t for _, t in self.owner.all_tasks()]
        # Empty time sorts after any real time because "" < "00:00" otherwise.
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    # --- filtering ---------------------------------------------------------
    def filter_tasks(
        self, pet_name: str | None = None, done: bool | None = None
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        result = []
        for pet, task in self.owner.all_tasks():
            if pet_name is not None and pet.name != pet_name:
                continue
            if done is not None and task.done != done:
                continue
            result.append(task)
        return result

    # --- recurring tasks ---------------------------------------------------
    def complete_task(self, pet: Pet, task: Task) -> Task | None:
        """Mark a task complete and queue its next occurrence if recurring."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet.add_task(upcoming)
        return upcoming

    # --- conflict detection ------------------------------------------------
    def detect_conflicts(self) -> list[str]:
        """Return warning strings for tasks sharing the same start time."""
        by_time: dict[str, list[str]] = {}
        for pet, task in self.owner.all_tasks():
            if task.time and not task.done:
                by_time.setdefault(task.time, []).append(f"{task.name} ({pet.name})")
        return [
            f"Conflict at {t}: {', '.join(names)} overlap."
            for t, names in by_time.items()
            if len(names) > 1
        ]

    # --- daily plan --------------------------------------------------------
    def _sorted_tasks(self) -> list[tuple[Pet, Task]]:
        """Return pending tasks sorted by priority (desc) then duration (asc)."""
        pending = [(p, t) for p, t in self.owner.all_tasks() if not t.done]
        return sorted(
            pending,
            key=lambda pt: (-pt[1].priority_value(), pt[1].duration_min),
        )

    def build_plan(self) -> list[tuple[Pet, Task]]:
        """Return the ordered tasks that fit the owner's daily time budget."""
        plan: list[tuple[Pet, Task]] = []
        self._last_skipped = []
        remaining = self.owner.minutes_available
        for pet, task in self._sorted_tasks():
            if task.duration_min <= remaining:
                plan.append((pet, task))
                remaining -= task.duration_min
            else:
                self._last_skipped.append((pet, task))
        return plan

    def explain(self) -> str:
        """Return a human-readable explanation of the most recent plan."""
        plan = self.build_plan()
        used = sum(t.duration_min for _, t in plan)
        lines = [
            f"Planned {len(plan)} task(s) using {used} of "
            f"{self.owner.minutes_available} available minutes, "
            "ordered by priority then shortest duration.",
        ]
        if self._last_skipped:
            skipped = ", ".join(t.name for _, t in self._last_skipped)
            lines.append(f"Skipped (not enough time): {skipped}.")
        return "\n".join(lines)
