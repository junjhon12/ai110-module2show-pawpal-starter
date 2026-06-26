"""Demo / testing-ground script for PawPal+ (CLI-first verification).

Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler) -> None:
    """Print a readable 'Today's Schedule' for the owner."""
    owner = scheduler.owner
    plan = scheduler.build_plan()

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    if not plan:
        print("  (no tasks planned)")
    for i, (pet, task) in enumerate(plan, start=1):
        status = "done" if task.done else "todo"
        print(
            f"  {i}. {task.name} for {pet.name} "
            f"({task.duration_min} min) [priority: {task.priority}] [{status}]"
        )
    print("-" * 40)
    print(scheduler.explain())


def main() -> None:
    owner = Owner(name="Quoc", minutes_available=60, preferences=["mornings"])

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mittens = Pet(name="Mittens", species="cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    biscuit.add_task(Task("Morning walk", duration_min=30, priority="high"))
    biscuit.add_task(Task("Feeding", duration_min=10, priority="high"))
    mittens.add_task(Task("Feeding", duration_min=10, priority="medium"))
    mittens.add_task(Task("Play / enrichment", duration_min=20, priority="low"))

    scheduler = Scheduler(owner)
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
