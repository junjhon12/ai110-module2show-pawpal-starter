"""Automated test suite for PawPal+.

Covers core behaviors (happy paths) and edge cases:
- Task completion and addition
- Sorting tasks chronologically
- Filtering by pet / status
- Recurring-task generation
- Conflict detection
- Empty / no-task edge cases
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def _owner_with(tasks):
    """Build an Owner with one pet ('Biscuit') holding the given tasks."""
    pet = Pet(name="Biscuit", species="dog")
    for t in tasks:
        pet.add_task(t)
    owner = Owner(name="Quoc")
    owner.add_pet(pet)
    return owner, pet


# --- core behaviors --------------------------------------------------------
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


# --- sorting ---------------------------------------------------------------
def test_sort_by_time_orders_chronologically():
    """sort_by_time() returns tasks in ascending HH:MM order."""
    owner, _ = _owner_with([
        Task("Evening", 30, time="18:00"),
        Task("Noon", 10, time="12:00"),
        Task("Morning", 30, time="08:00"),
    ])
    names = [t.name for t in Scheduler(owner).sort_by_time()]
    assert names == ["Morning", "Noon", "Evening"]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks with no time sort after timed tasks instead of first."""
    owner, _ = _owner_with([
        Task("Untimed", 10, time=""),
        Task("Morning", 30, time="08:00"),
    ])
    names = [t.name for t in Scheduler(owner).sort_by_time()]
    assert names == ["Morning", "Untimed"]


# --- filtering -------------------------------------------------------------
def test_filter_by_done_status():
    """filter_tasks(done=True) returns only completed tasks."""
    done = Task("A", 10)
    done.mark_complete()
    owner, _ = _owner_with([done, Task("B", 10)])
    assert [t.name for t in Scheduler(owner).filter_tasks(done=True)] == ["A"]


def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) returns only that pet's tasks."""
    owner, _ = _owner_with([Task("Walk", 30)])
    mittens = Pet(name="Mittens", species="cat")
    mittens.add_task(Task("Feed cat", 10))
    owner.add_pet(mittens)
    assert [t.name for t in Scheduler(owner).filter_tasks(pet_name="Mittens")] == ["Feed cat"]


# --- recurrence ------------------------------------------------------------
def test_complete_daily_task_creates_next_day_occurrence():
    """Completing a daily task queues a fresh copy due exactly one day later."""
    today = date.today()
    owner, pet = _owner_with([Task("Walk", 30, frequency="daily", due_date=today)])
    upcoming = Scheduler(owner).complete_task(pet, pet.tasks[0])
    assert upcoming is not None
    assert upcoming.done is False
    assert upcoming.due_date == today + timedelta(days=1)
    assert len(pet.tasks) == 2


def test_complete_once_task_does_not_recur():
    """A non-recurring task does not generate a follow-up occurrence."""
    owner, pet = _owner_with([Task("Vet visit", 60, frequency="once")])
    upcoming = Scheduler(owner).complete_task(pet, pet.tasks[0])
    assert upcoming is None
    assert len(pet.tasks) == 1


# --- conflict detection ----------------------------------------------------
def test_detect_conflicts_flags_same_time():
    """detect_conflicts() warns when two tasks share a start time."""
    owner, _ = _owner_with([
        Task("Walk", 30, time="08:00"),
        Task("Feed", 10, time="08:00"),
    ])
    assert len(Scheduler(owner).detect_conflicts()) == 1


def test_no_conflict_for_distinct_times():
    """Tasks at different times produce no conflict warnings."""
    owner, _ = _owner_with([
        Task("Walk", 30, time="08:00"),
        Task("Feed", 10, time="12:00"),
    ])
    assert Scheduler(owner).detect_conflicts() == []


# --- edge cases ------------------------------------------------------------
def test_pet_with_no_tasks_plans_empty():
    """A pet with no tasks yields an empty plan and no conflicts."""
    owner, _ = _owner_with([])
    scheduler = Scheduler(owner)
    assert scheduler.build_plan() == []
    assert scheduler.detect_conflicts() == []


def test_build_plan_skips_tasks_over_time_budget():
    """build_plan() drops tasks that do not fit the remaining minutes."""
    owner, _ = _owner_with([Task("Long walk", 120, priority="high")])
    owner.minutes_available = 30
    assert Scheduler(owner).build_plan() == []
