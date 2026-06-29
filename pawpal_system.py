from dataclasses import dataclass, field
from typing import List

@dataclass
class Task:
    """Represents a single care activity."""
    id: str
    description: str
    time: str  # Format: "HH:MM"
    frequency: str = "Once" # "Once", "Daily", or "Weekly"
    is_complete: bool = False

    def mark_complete(self) -> None:
        pass

@dataclass
class Pet:
    """Represents a pet profile and their specific tasks."""
    id: str
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

@dataclass
class Owner:
    """Represents the user and manages their pets."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[tuple]:
        pass

class Scheduler:
    """The brain that organizes tasks across all pets."""
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_sorted_tasks(self) -> List[tuple]:
        pass

    def check_conflicts(self) -> List[str]:
        pass