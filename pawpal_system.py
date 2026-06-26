"""PawPal+ logic layer (backend classes).

Phase 1 skeleton: class names, attributes, and empty method stubs only.
Logic will be filled in during later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care task (e.g., a walk, feeding, meds)."""

    name: str
    duration_min: int
    priority: str = "medium"  # "low" | "medium" | "high"
    done: bool = False

    def mark_done(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by the user, with its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner, including their daily time budget and preferences."""

    name: str
    minutes_available: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def list_pets(self) -> list[Pet]:
        """Return all pets owned by this user."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily plan from tasks, respecting time and priority."""

    def __init__(self, minutes_available: int, preferences: list[str] | None = None):
        self.minutes_available = minutes_available
        self.preferences = preferences or []

    def build_plan(self, tasks: list[Task]) -> list[Task]:
        """Return an ordered subset of tasks that fits the time budget."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of the chosen plan."""
        raise NotImplementedError
