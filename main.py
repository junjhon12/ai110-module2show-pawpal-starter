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

    # Tasks added intentionally OUT OF TIME ORDER to exercise sorting.
    biscuit.add_task(Task("Evening walk", 30, "high", "daily", time="18:00"))
    biscuit.add_task(Task("Morning walk", 30, "high", "daily", time="08:00"))
    biscuit.add_task(Task("Feeding", 10, "high", "daily", time="08:00"))  # conflict @08:00
    mittens.add_task(Task("Feeding", 10, "medium", "daily", time="12:00"))
    mittens.add_task(Task("Play / enrichment", 20, "low", "weekly", time="15:00"))

    scheduler = Scheduler(owner)

    print_schedule(scheduler)

    print("\nTasks sorted by time:")
    for t in scheduler.sort_by_time():
        print(f"  {t.time or '--:--'}  {t.name}")

    print("\nFilter — Biscuit's tasks:")
    for t in scheduler.filter_tasks(pet_name="Biscuit"):
        print(f"  {t.name}")

    print("\nConflict detection:")
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts or ["  (none)"]:
        print(f"  {warning}")

    print("\nRecurring tasks — completing Biscuit's morning walk:")
    morning = next(t for t in biscuit.tasks if t.name == "Morning walk")
    upcoming = scheduler.complete_task(biscuit, morning)
    print(f"  Completed: {morning.name} (done={morning.done})")
    print(f"  Next occurrence due: {upcoming.due_date} (done={upcoming.done})")

    print("\nFilter — completed tasks now:")
    for t in scheduler.filter_tasks(done=True):
        print(f"  {t.name}")


if __name__ == "__main__":
    main()
