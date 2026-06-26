"""PawPal+ logic layer (backend classes).

Phase 2: full implementation of the core classes, verified CLI-first
(via main.py) before being wired into the Streamlit UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Priority labels ranked so higher numbers schedule first.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""

    name: str
    duration_min: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "daily"  # e.g. "daily", "weekly"
    done: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def priority_value(self) -> int:
        """Return the numeric rank of this task's priority (higher = sooner)."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)


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
    """Builds a daily plan from an owner's tasks, respecting time and priority."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self._last_skipped: list[tuple[Pet, Task]] = []

    def _sorted_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all pending tasks sorted by priority (desc) then duration (asc)."""
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
