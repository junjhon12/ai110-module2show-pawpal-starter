# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ implements the following scheduling logic (see `pawpal_system.py`):

- **Owner / Pet / Task model** — an owner manages multiple pets, each with its own list of care tasks (name, duration, priority, time, frequency).
- **Priority-aware daily planning** — `Scheduler.build_plan()` orders tasks by priority, then shortest duration, and packs them into the owner's available minutes.
- **Plan explanations** — `Scheduler.explain()` reports how many minutes were used and which tasks were skipped for lack of time.
- **Chronological sorting** — `Scheduler.sort_by_time()` lists tasks in `HH:MM` order (untimed tasks last).
- **Filtering** — `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags tasks that share a start time, returning friendly warnings instead of crashing.
- **Recurring tasks** — completing a `daily`/`weekly` task (`Scheduler.complete_task()` + `Task.next_occurrence()`) automatically queues the next occurrence (+1 / +7 days via `timedelta`).

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule for Quoc
========================================
  1. Feeding for Biscuit (10 min) [priority: high] [todo]
  2. Morning walk for Biscuit (30 min) [priority: high] [todo]
  3. Feeding for Mittens (10 min) [priority: medium] [todo]
----------------------------------------
Planned 3 task(s) using 50 of 60 available minutes, ordered by priority then shortest duration.
Skipped (not enough time): Play / enrichment.
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 12 tests):

- **Core behaviors** — marking a task complete flips its status; adding a task grows the pet's task list.
- **Sorting** — tasks return in chronological `HH:MM` order, with untimed tasks placed last.
- **Filtering** — `filter_tasks()` narrows by pet name and by completion status.
- **Recurrence** — completing a `daily` task queues a fresh copy due exactly one day later; a `once` task does not recur.
- **Conflict detection** — duplicate start times raise a warning; distinct times do not.
- **Edge cases** — a pet with no tasks plans empty (no crash); tasks longer than the time budget are skipped.

Successful run:

```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0
collected 12 items

tests\test_pawpal.py ............                                        [100%]

============================= 12 passed in 0.07s ==============================
```

**Confidence level:** ⭐⭐⭐⭐☆ (4/5) — all core logic (sorting, filtering, recurrence,
conflict detection) is covered by passing tests, including key edge cases. Held back
from 5/5 because conflict detection only checks exact time matches (not duration
overlaps), and time-zone / date-rollover behavior around recurrence is not yet tested.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by "HH:MM" start time; untimed tasks sort last. `build_plan()` separately orders by priority then duration to fit the time budget. |
| Filtering | `Scheduler.filter_tasks(pet_name, done)` | Filter tasks by pet name and/or completion status (either or both). |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight check: returns warning strings (never raises) when two active tasks share the same start time. |
| Recurring tasks | `Scheduler.complete_task()` + `Task.next_occurrence()` | Completing a `daily`/`weekly` task auto-queues a fresh copy due +1 / +7 days (via `timedelta`). |

## 📸 Demo Walkthrough

Launch the app with `streamlit run app.py`.

### Main UI features

- **Owner panel** — set your name and the minutes you have available today.
- **Add a Pet** — enter name, species, and optional breed.
- **Add a Task** — pick a pet, then set title, duration, priority, start time (`HH:MM`), and frequency (`daily` / `weekly` / `once`).
- **Your Pets** — each pet's tasks are listed with a **Done** button; completing a recurring task auto-queues its next occurrence.
- **Today's Schedule** — conflict warnings appear at the top, then **Generate schedule** shows the prioritized plan, an explanation, and the full day sorted by time.

### Example workflow

1. Set owner **Quoc** with **60** available minutes.
2. Add a pet → **Biscuit** (dog, Golden Retriever).
3. Add tasks → "Morning walk" 08:00 (high), "Feeding" 08:00 (high), "Evening walk" 18:00 (high).
4. A ⚠️ conflict warning appears for the two **08:00** tasks.
5. Click **Generate schedule** → tasks are ordered by priority within the 60-minute budget, the explanation lists anything skipped, and the full timeline is sorted chronologically.
6. Click **Done** on "Morning walk" → it is marked complete and tomorrow's occurrence is queued automatically.

### Scheduler behaviors shown

- **Sorting** by start time (`sort_by_time`)
- **Priority + time-budget planning** (`build_plan`, `explain`)
- **Conflict warnings** for duplicate times (`detect_conflicts`)
- **Daily/weekly recurrence** on completion (`complete_task`, `next_occurrence`)

### Sample CLI output (`python main.py`)

```
Today's Schedule for Quoc
========================================
  1. Feeding for Biscuit (10 min) [priority: high] [todo]
  2. Evening walk for Biscuit (30 min) [priority: high] [todo]
  3. Feeding for Mittens (10 min) [priority: medium] [todo]
----------------------------------------
Planned 3 task(s) using 50 of 60 available minutes, ordered by priority then shortest duration.
Skipped (not enough time): Morning walk, Play / enrichment.

Tasks sorted by time:
  08:00  Morning walk
  08:00  Feeding
  12:00  Feeding
  15:00  Play / enrichment
  18:00  Evening walk

Conflict detection:
  Conflict at 08:00: Morning walk (Biscuit), Feeding (Biscuit) overlap.

Recurring tasks - completing Biscuit's morning walk:
  Completed: Morning walk (done=True)
  Next occurrence due: 2026-06-26 (done=False)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
