from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple
from datetime import date, timedelta
import json

@dataclass
class Task:
    """Represents a single care activity."""
    name: str
    duration_min: int = 0
    time: str = ""  # Format: "HH:MM"
    priority: str = "medium"
    frequency: str = "once"
    due_date: Optional[date] = None
    done: bool = False

    def mark_complete(self) -> None:
        self.done = True

@dataclass
class Pet:
    """Represents a pet profile, their tasks, and RPG stats."""
    name: str
    species: str
    breed: str = ""
    age: int = 1
    # RPG Stats for Streamlit UI
    xp: int = 0
    level: int = 1
    health: str = "good"
    mood: str = "happy"
    speed: int = 5
    endurance: int = 5
    intelligence: int = 5
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        
    def xp_to_next(self) -> int:
        return self.level * 100
        
    def xp_progress(self) -> float:
        return min(self.xp / self.xp_to_next(), 1.0)
        
    def add_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1
            return True
        return False

@dataclass
class Owner:
    """Represents the user and manages their pets and time budget."""
    name: str = "Player"
    minutes_available: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)
        
    def save_to_json(self, path: str):
        """Serializes the object graph to JSON."""
        data = {
            "name": self.name,
            "minutes_available": self.minutes_available,
            "pets": [
                {
                    "name": p.name,
                    "species": p.species,
                    "breed": p.breed,
                    "age": p.age,
                    "xp": p.xp,
                    "level": p.level,
                    "tasks": [
                        {
                            "name": t.name,
                            "duration_min": t.duration_min,
                            "time": t.time,
                            "priority": t.priority,
                            "frequency": t.frequency,
                            "due_date": t.due_date.isoformat() if t.due_date else None,
                            "done": t.done
                        } for t in p.tasks
                    ]
                } for p in self.pets
            ]
        }
        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def load_from_json(cls, path: str):
        """Rebuilds the Owner and nested Pets/Tasks from JSON."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            owner = cls(name=data["name"], minutes_available=data.get("minutes_available", 120))
            
            for p_data in data.get("pets", []):
                pet = Pet(
                    name=p_data["name"], 
                    species=p_data["species"],
                    breed=p_data.get("breed", ""),
                    age=p_data.get("age", 1),
                    xp=p_data.get("xp", 0),
                    level=p_data.get("level", 1)
                )
                for t_data in p_data.get("tasks", []):
                    due_date = date.fromisoformat(t_data["due_date"]) if t_data.get("due_date") else None
                    pet.add_task(Task(
                        name=t_data["name"],
                        duration_min=t_data.get("duration_min", 0),
                        time=t_data.get("time", ""),
                        priority=t_data.get("priority", "medium"),
                        frequency=t_data.get("frequency", "once"),
                        due_date=due_date,
                        done=t_data.get("done", False)
                    ))
                owner.add_pet(pet)
            return owner
        except FileNotFoundError:
            return None

class Scheduler:
    """The algorithmic brain of PawPal+."""
    def __init__(self, owner: Owner):
        self.owner = owner

    def _get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        return [(p, t) for p in self.owner.pets for t in p.tasks]

    def sort_by_time(self) -> List[Task]:
        """Returns all tasks in chronological order, untimed tasks last."""
        tasks = [t for p, t in self._get_all_tasks()]
        return sorted(tasks, key=lambda t: t.time if t.time else "99:99")

    def filter_tasks(self, pet_name: str = None, done: bool = None) -> List[Task]:
        """Filters tasks by pet or completion status."""
        tasks = []
        for p, t in self._get_all_tasks():
            match_pet = (pet_name is None) or (p.name == pet_name)
            match_done = (done is None) or (t.done == done)
            if match_pet and match_done:
                tasks.append(t)
        return tasks

    def complete_task(self, pet: Pet, task: Task) -> Optional[Task]:
        """Marks a task complete and queues the next occurrence if recurring."""
        task.mark_complete()
        if task.frequency.lower() in ["daily", "weekly"]:
            days = 1 if task.frequency.lower() == "daily" else 7
            base_date = task.due_date if task.due_date else date.today()
            new_task = replace(task, done=False, due_date=base_date + timedelta(days=days))
            pet.add_task(new_task)
            return new_task
        return None

    def detect_conflicts(self) -> List[str]:
        """Flags tasks that share an exact start time."""
        times = {}
        conflicts = []
        for p, t in self._get_all_tasks():
            if not t.time or t.done:
                continue
            if t.time in times:
                conflicts.append(f"Conflict at {t.time}: {t.name} and {times[t.time].name} overlap.")
            else:
                times[t.time] = t
        return conflicts

    def build_plan(self) -> List[Tuple[Pet, Task]]:
        """Schedules tasks considering priority and available time budget."""
        active = [(p, t) for p, t in self._get_all_tasks() if not t.done]
        pri_map = {"high": 1, "medium": 2, "low": 3}
        # Sort by: Priority -> Time -> Shortest Duration
        active.sort(key=lambda x: (pri_map.get(x[1].priority.lower(), 4), x[1].time if x[1].time else "99:99", x[1].duration_min))

        plan = []
        used_min = 0
        for p, t in active:
            if used_min + t.duration_min <= self.owner.minutes_available:
                plan.append((p, t))
                used_min += t.duration_min
        return plan

    def next_available_slot(self, duration_min: int, day_start="08:00", day_end="21:00") -> Optional[str]:
        """Algorithm to find the first free gap of time in the schedule."""
        def to_min(t_str):
            h, m = map(int, t_str.split(':'))
            return h * 60 + m
        def to_str(m_int):
            return f"{m_int // 60:02d}:{m_int % 60:02d}"

        active = sorted([t for p, t in self._get_all_tasks() if not t.done and t.time], key=lambda x: x.time)
        curr_min = to_min(day_start)
        
        for t in active:
            t_start = to_min(t.time)
            if t_start >= curr_min + duration_min:
                return to_str(curr_min)
            curr_min = max(curr_min, t_start + t.duration_min)
        
        if to_min(day_end) >= curr_min + duration_min:
            return to_str(curr_min)
        return None
        
    def explain(self) -> str:
        """Explains how the schedule was calculated for the UI."""
        used = sum(t.duration_min for p, t in self.build_plan())
        skipped = [t.name for p, t in self._get_all_tasks() if not t.done and (p, t) not in self.build_plan()]
        msg = f"Planned {len(self.build_plan())} quest(s) using {used} of {self.owner.minutes_available} available minutes."
        if skipped:
            msg += f" Skipped (not enough energy): {', '.join(skipped)}."
        return msg