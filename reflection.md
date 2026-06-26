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

- _To be completed as I implement and refine the design._

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
