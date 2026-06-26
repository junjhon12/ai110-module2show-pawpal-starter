# AI Interactions Log

> **Stretch features only.** Documents the AI-assisted work for the stretch challenges.

---

## Agent Workflow (SF7 / Challenge 1)

> Documenting the agent run that added the third algorithmic capability
> (`next_available_slot`) and the supporting challenge features.

**What task did you give the agent?**

"Add a third scheduling capability — a `next_available_slot` method that finds the
earliest free gap in the day for a task of a given length — plus JSON persistence,
priority-then-time planning, and a professionally formatted CLI. Update the tests and
docs to match."

**What did the agent do?**

Files modified:

- `pawpal_system.py` — added `next_available_slot()` (interval-scan over occupied time
  blocks), `to_dict` / `from_dict` / `save_to_json` / `load_from_json`, the `_to_minutes`
  / `_to_hhmm` helpers, and changed `_sorted_tasks()` to sort by priority → time → duration.
- `main.py` — rewrote the demo to use `tabulate`, emojis, and ANSI color, and to
  demonstrate the next-slot search and a save/load round-trip.
- `app.py` — load from `data.json` on startup, re-save after each mutation, and added a
  "Find the next free slot" expander.
- `tests/test_pawpal.py` — added tests for priority-then-time ordering, next-slot search,
  persistence round-trip, and missing-file handling (16 tests total, all passing).
- `requirements.txt` (added `tabulate`), `.gitignore` (ignore `data.json`),
  `diagrams/uml_final.mmd`, and `README.md`.

**What did you have to verify or fix manually?**

- **Windows encoding:** the first run crashed with `UnicodeEncodeError` because the
  Windows console is cp1252 and could not print emojis/box-drawing. Fixed by adding
  `sys.stdout.reconfigure(encoding="utf-8")` at the top of `main.py`.
- **Untimed-task ordering:** confirmed empty `time` values sort *after* real times by
  using a `"99:99"` sentinel in the sort key, rather than letting `""` sort first.
- **Date serialization:** verified `due_date` round-trips correctly by storing
  `.isoformat()` strings and parsing them back with `date.fromisoformat()`; covered by a
  persistence test.

---

## Prompt Comparison (SF11 / Challenge 5)

> Task compared: **the logic for rescheduling a recurring (weekly) task when it is
> marked complete.** Two candidate solutions were generated and evaluated.

> ⚠️ Transparency note: this work was done inside a Claude Code session, so both
> candidates below were produced by **Claude**. Option B is left as a template for a
> second tool (e.g., Gemini / ChatGPT / Copilot) — paste that model's output there to
> complete a true cross-model comparison.

| | Option A (used) | Option B (to compare) |
|-|------------------|------------------------|
| **Model / tool used** | Claude (Opus 4.8, via Claude Code) | _e.g., Gemini / ChatGPT / Copilot — fill in_ |
| **Prompt** | "When a daily/weekly task is marked complete, create the next occurrence. Keep the completed task in history." | _your prompt for the other model_ |
| **Response summary** | Keep completion and recurrence separate: `mark_complete()` flips the original to done; `next_occurrence()` returns a fresh `dataclasses.replace()` copy with `due_date = base + timedelta(days=1 or 7)` and `done=False`; `Scheduler.complete_task()` appends it. | _summary of the other model's answer_ |
| **What was useful** | Immutable copy preserves history; `timedelta` handles date math (incl. month boundaries) correctly; easy to unit-test. | _what was good about it_ |
| **Problems noticed** | An earlier draft mutated `due_date` in place, which would have erased the completed record — rejected. | _what was flawed_ |
| **Decision** | ✅ Adopted the immutable-copy approach. | _your call_ |

**Which approach did you use in your final implementation and why?**

I used the **immutable-copy** approach (Option A). Returning a new `Task` via
`dataclasses.replace()` keeps the completed task visible in history while queuing the next
occurrence, and using `timedelta` for the date arithmetic correctly handles week/month
rollovers. It is also the easiest to verify — a single test asserts the new task is
`done == False` and due exactly one cycle later. The rejected in-place-mutation variant
was simpler but destroyed the completion record, which would break the "Done" history in
the UI.
