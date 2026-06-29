from pawpal_system import Task, Pet, Owner, Scheduler

owner = Owner(name="Jordan", minutes_available=120)
dog = Pet(name="Mochi", species="Dog")
cat = Pet(name="Luna", species="Cat")
owner.add_pet(dog)
owner.add_pet(cat)

dog.add_task(Task(name="Morning Walk", duration_min=30, time="08:00", priority="high", frequency="Daily"))
dog.add_task(Task(name="Dinner", duration_min=15, time="18:00", priority="high", frequency="Daily"))
cat.add_task(Task(name="Clean Litterbox", duration_min=10, time="09:00", priority="medium", frequency="Weekly"))

scheduler = Scheduler(owner=owner)
schedule = scheduler.build_plan()

print(f"\n--- Today's Schedule for {owner.name}'s Pets ---")
for pet, task in schedule:
    status = "[X]" if task.done else "[ ]"
    print(f"{status} {task.time} - {pet.name}: {task.name} ({task.duration_min} min | Priority: {task.priority})")
print("------------------------------------------\n")
print(scheduler.explain())