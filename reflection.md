# PawPal+ Project Reflection

## 1. System Design
**Core user actions:**
1. Add a pet (name, species, RPG stats).
2. Add or edit care tasks for a pet (with duration, time, and priority).
3. Generate a daily plan that fits the owner's available time and explains its choices.

**a. Initial design**
I chose four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`. Relationships: an Owner *has* many Pets, a Pet *has* many Tasks, and the Scheduler *operates on* the Owner to build the plan. I kept the scheduling logic separate from the data classes so the planning algorithms could scale without bloating the `Pet` or `Task` objects.

**b. Design changes**
During the build, we added RPG attributes (`xp`, `level`, `health`) to the `Pet` class to support the Streamlit UI's gamification. I also added `minutes_available` to the `Owner` class so the `Scheduler` could calculate a time budget directly from the owner's profile.

## 2. Scheduling Logic and Tradeoffs
**a. Constraints and priorities**
The scheduler considers three constraints: the owner's available time budget, task priority, and task duration. The `build_plan()` algorithm sorts tasks by priority first, then by start time, and finally by shortest duration. It adds tasks to the plan until the owner's time budget runs out.

**b. Tradeoffs**
My conflict detection (`Scheduler.detect_conflicts()`) only flags tasks that share the *exact same start time*—it does not calculate whether two tasks overlap based on their durations. I chose this exact-match approach because it is lightweight, fast, and catches the most common user errors (e.g., accidentally scheduling two tasks at exactly 08:00). The tradeoff is that subtle duration overlaps might slip through, but since this app is a planning aid rather than a strict enforcer, a warning system is sufficient.

## 3. AI Collaboration
**a. How you used AI**
I used my AI coding assistant across every phase: generating the Mermaid UML, scaffolding the logic layer, troubleshooting testing errors, and fixing terminal PATH issues when Streamlit failed to run.

**b. Judgment and verification**
One AI suggestion I modified was during the testing phase. The AI originally suggested stripping out the starter repository's advanced test suite because it was throwing errors. Instead of deleting the tests, I used the AI to help me upgrade my `pawpal_system.py` data models (adding `duration_min`, `priority`, etc.) so that my code could satisfy the rigorous, advanced tests. 

## 4. Reflection
The biggest lesson I learned about being the "lead architect" when collaborating with AI is that you have to manage the scope and context. Using separate chat sessions for different phases kept the AI focused on the immediate problem (like fixing a specific `pytest` failure) without getting confused by previous frontend code. The AI is a powerful generator, but as the architect, I had to ensure its generated code actually matched the strict requirements of my pre-existing test suite and UI.