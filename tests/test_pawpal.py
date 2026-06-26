"""Quick tests for PawPal+ core behaviors."""

from pawpal_system import Pet, Task


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
