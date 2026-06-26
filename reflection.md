# PawPal+ Project Reflection

## 1. System Design

**Core user actions** (three things a user should be able to do):

1. Add a pet (name, species, breed).
2. Add or edit care tasks for a pet (with a duration and a priority).
3. Generate a daily plan that fits the owner's available time and explains its choices.

**a. Initial design**

I chose four classes:

- **Owner** — the user. Holds their name, daily time budget (`minutes_available`),
  preferences, and the list of pets. Responsible for managing pets.
- **Pet** — a single animal. Holds name/species/breed and its own list of tasks.
  Responsible for adding/removing its care tasks.
- **Task** — one care item (walk, feeding, meds). Holds name, duration, priority,
  and done-state. A dataclass since it is mostly data.
- **Scheduler** — the brains. Takes a list of tasks plus the time budget and
  preferences, and produces an ordered daily plan it can explain.

Relationships: an Owner *has* many Pets, a Pet *has* many Tasks, and the Scheduler
*operates on* Tasks to build the plan. I kept scheduling logic separate from the
data classes so the planning rules can change without touching Pet/Task.

**b. Design changes**

The design held up well, but a few things changed during the build:

- I renamed `Task.mark_done()` to `mark_complete()` to match the testing requirements
  and read more naturally in the UI.
- I added attributes the scheduler actually needed: `time` (`HH:MM`) so tasks can be
  sorted chronologically and checked for conflicts, and `due_date` + `frequency` so
  recurring tasks could regenerate themselves.
- I added `Owner.all_tasks()` so the `Scheduler` could pull every task across all pets
  through one clean method instead of reaching into each pet's list. This kept the
  Scheduler decoupled from how pets store their tasks.
- The `Scheduler` ended up taking the whole `Owner` (rather than a loose list of tasks),
  which let it read the time budget and all pets from a single source of truth.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: the owner's **available minutes** for the day,
each task's **priority** (high/medium/low), and each task's **duration**. `build_plan()`
sorts tasks by priority first, then by shortest duration, and adds them one at a time only
while they still fit the remaining minutes. I decided **time budget** mattered most because
it is a hard limit — a plan that does not fit the day is useless — and **priority** came
second so the most important care (meds, walks) is never dropped in favor of optional tasks.
Duration is a tiebreaker so that, among equally important tasks, the scheduler can fit more
of them in. Owner preferences are stored but currently only used as soft context.

**b. Tradeoffs**

My conflict detection (`Scheduler.detect_conflicts()`) only flags tasks that share
the **exact same start time** — it does not check whether two tasks *overlap* based on
their durations (e.g., an 08:00 task lasting 30 min running into an 08:15 task). I chose
exact-match because it is simple, fast, and easy to reason about, and because most
everyday pet-care tasks are entered on round, recurring times (08:00, 12:00, 18:00),
so exact collisions catch the common case. The tradeoff is that subtle overlaps slip
through. That is reasonable for this scenario: the app is a planning aid, not a
hard real-time scheduler, and it warns rather than blocks — so the owner still makes
the final call. Duration-aware overlap detection is a clear next step if needed.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase: brainstorming the class list and
Mermaid UML, scaffolding the dataclass skeletons, implementing the sorting/filtering/
recurrence/conflict algorithms, drafting the pytest suite, and writing documentation.
The most effective features were **agent/multi-file editing** (it could update
`pawpal_system.py`, `main.py`, and the tests together so the recurrence change stayed
consistent) and **inline chat on a specific method** to ask "how do I sort `HH:MM`
strings with a `sorted()` key?" The most helpful prompts were narrow and concrete —
naming the method, the file, and the exact behavior I wanted — rather than vague
"make this better" requests.

**b. Judgment and verification**

One AI suggestion I modified: for recurring tasks it first proposed mutating the
original `Task` in place (moving its `due_date` forward). I rejected that because it
would lose the history of the completed task and make it impossible to show "done"
items. Instead I kept completion and recurrence separate — `mark_complete()` flips the
original to done, and `next_occurrence()` returns a fresh `replace()`d copy. I verified
behavior by writing a test asserting the new task is `done == False` and due exactly
`today + 1 day`, and by running `main.py` to watch a completed walk spawn tomorrow's
occurrence. I treated AI output as a draft to be checked against tests, never as
trusted-by-default.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 12 pytest tests covering: task completion flipping status, adding a task growing
the pet's list, chronological sorting (and untimed tasks sorting last), filtering by pet
name and by done-status, daily recurrence creating a next-day copy, a `once` task *not*
recurring, conflict detection flagging duplicate times (and staying silent for distinct
times), and edge cases like a pet with no tasks and a task larger than the time budget.
These mattered because sorting, recurrence, and conflict detection are the "smart" parts
most likely to break silently, and the edge cases confirm the app degrades gracefully
instead of crashing.

**b. Confidence**

I am fairly confident — 4 out of 5. Every core behavior is covered by a passing test,
including the main edge cases. I held back from full confidence because conflict
detection only checks exact time matches (not duration overlaps), and I have not tested
date rollover or time-zone behavior around recurrence. With more time I would test
overlapping-duration conflicts, weekly recurrence math across month boundaries, and
invalid time strings (e.g., "8am") to make input handling more robust.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the clean separation between the logic layer
(`pawpal_system.py`) and the UI (`app.py`). Building and verifying the "brain" in
`main.py` and pytest first meant that wiring it into Streamlit was mostly about display,
not debugging logic. The recurring-task feature also came together cleanly because the
data model already had `frequency` and `due_date`.

**b. What you would improve**

I would upgrade conflict detection to be duration-aware (true overlap, not just exact
start-time matches), validate time input in the UI, and let owner preferences actually
influence the plan (e.g., favoring morning tasks). I would also persist data to disk so
a plan survives closing the app.

**c. Key takeaway**

The biggest lesson was what it means to be the **lead architect** while collaborating
with a powerful AI. The AI is excellent at generating options and boilerplate fast, but
it does not own the design — I do. My job was to set the structure (four classes, logic
separated from UI), give precise prompts, and verify every suggestion against tests and
the actual scenario, rejecting the ones that added complexity or hurt readability.
Using **separate chat sessions per phase** (design, algorithms, testing) kept each
conversation focused and stopped earlier context from muddying later decisions. The AI
made me faster; staying the architect kept the system coherent.
