"""Quick tests for PawPal+ core behaviors."""

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from not-done to done."""
    task = Task("Walk", duration_min=30, priority="high")
    assert task.done is False
    task.mark_complete()
    assert task.done is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", duration_min=10))
    assert len(pet.tasks) == 1


def _owner_with(tasks):
    """Build an Owner with one pet holding the given tasks."""
    pet = Pet(name="Biscuit", species="dog")
    for t in tasks:
        pet.add_task(t)
    owner = Owner(name="Quoc")
    owner.add_pet(pet)
    return owner, pet


def test_sort_by_time_orders_hh_mm():
    """sort_by_time() returns tasks in ascending HH:MM order."""
    owner, _ = _owner_with([
        Task("Evening", 30, time="18:00"),
        Task("Morning", 30, time="08:00"),
    ])
    names = [t.name for t in Scheduler(owner).sort_by_time()]
    assert names == ["Morning", "Evening"]


def test_filter_by_done_status():
    """filter_tasks(done=True) returns only completed tasks."""
    done = Task("A", 10)
    done.mark_complete()
    owner, _ = _owner_with([done, Task("B", 10)])
    assert [t.name for t in Scheduler(owner).filter_tasks(done=True)] == ["A"]


def test_detect_conflicts_flags_same_time():
    """detect_conflicts() warns when two tasks share a start time."""
    owner, _ = _owner_with([
        Task("Walk", 30, time="08:00"),
        Task("Feed", 10, time="08:00"),
    ])
    assert len(Scheduler(owner).detect_conflicts()) == 1


def test_complete_task_queues_next_occurrence():
    """Completing a daily task adds a fresh, not-done recurrence."""
    owner, pet = _owner_with([Task("Walk", 30, frequency="daily", time="08:00")])
    scheduler = Scheduler(owner)
    upcoming = scheduler.complete_task(pet, pet.tasks[0])
    assert upcoming is not None and upcoming.done is False
    assert len(pet.tasks) == 2
