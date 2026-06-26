"""Demo / testing-ground script for PawPal+ (CLI-first verification).

Showcases the smarter scheduler plus the challenge features:
priority-then-time planning, next-available-slot search, JSON persistence,
and professional formatting (emojis, color, tabulate tables).

Run with:  python main.py
"""

import sys

from tabulate import tabulate

from pawpal_system import Owner, Pet, Scheduler, Task

# Ensure emojis/box-drawing render on Windows terminals (default cp1252).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ANSI color codes for color-coded status in the terminal.
COLORS = {"high": "\033[91m", "medium": "\033[93m", "low": "\033[92m", "reset": "\033[0m"}

# Emoji per task type, inferred from the task name keywords.
TYPE_EMOJI = [
    ("walk", "🚶"), ("feed", "🍽️"), ("med", "💊"),
    ("play", "🎾"), ("groom", "✂️"), ("enrich", "🧩"),
]


def task_emoji(name: str) -> str:
    """Return an emoji that matches the task type, defaulting to a paw."""
    lowered = name.lower()
    for keyword, emoji in TYPE_EMOJI:
        if keyword in lowered:
            return emoji
    return "🐾"


def color_priority(priority: str) -> str:
    """Wrap a priority label in its ANSI color for terminal output."""
    return f"{COLORS.get(priority, '')}{priority}{COLORS['reset']}"


def print_schedule(scheduler: Scheduler) -> None:
    """Print 'Today's Schedule' as a formatted, color-coded table."""
    owner = scheduler.owner
    plan = scheduler.build_plan()

    print(f"\n📅 Today's Schedule for {owner.name}")
    if not plan:
        print("  (no tasks planned)")
        return

    rows = [
        [
            i,
            task.time or "--:--",
            f"{task_emoji(task.name)} {task.name}",
            pet.name,
            f"{task.duration_min} min",
            color_priority(task.priority),
            "✅" if task.done else "⬜",
        ]
        for i, (pet, task) in enumerate(plan, start=1)
    ]
    headers = ["#", "Time", "Task", "Pet", "Duration", "Priority", "Done"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print(scheduler.explain())


def main() -> None:
    owner = Owner(name="Quoc", minutes_available=60, preferences=["mornings"])

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mittens = Pet(name="Mittens", species="cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # Tasks added intentionally OUT OF ORDER to exercise priority+time sorting.
    biscuit.add_task(Task("Evening walk", 30, "high", "daily", time="18:00"))
    biscuit.add_task(Task("Morning walk", 30, "high", "daily", time="08:00"))
    biscuit.add_task(Task("Feeding", 10, "high", "daily", time="08:00"))  # conflict @08:00
    mittens.add_task(Task("Feeding", 10, "medium", "daily", time="12:00"))
    mittens.add_task(Task("Play / enrichment", 20, "low", "weekly", time="15:00"))

    scheduler = Scheduler(owner)

    print_schedule(scheduler)

    print("\n🔍 Conflict detection:")
    for warning in scheduler.detect_conflicts() or ["  (none)"]:
        print(f"  ⚠️ {warning}")

    # Challenge 1: next available slot.
    slot = scheduler.next_available_slot(duration_min=45)
    print(f"\n🕳️  Next free 45-min slot today: {slot}")

    # Challenge 2: persistence round-trip.
    owner.save_to_json("data.json")
    reloaded = Owner.load_from_json("data.json")
    print(
        f"\n💾 Saved to data.json and reloaded "
        f"{len(reloaded.pets)} pets, {len(reloaded.all_tasks())} tasks."
    )


if __name__ == "__main__":
    main()
