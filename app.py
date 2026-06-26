import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care based on time, priority, and conflicts.")

# --- Application memory & persistence --------------------------------------
# Streamlit re-runs this script top-to-bottom on every interaction, so we keep
# the Owner in st.session_state. On first load we restore from data.json (if it
# exists) so pets and tasks survive between app runs; mutations re-save.
DATA_FILE = "data.json"
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE) or Owner(
        name="Jordan", minutes_available=60
    )

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def save() -> None:
    """Persist the current owner (and all nested data) to disk."""
    owner.save_to_json(DATA_FILE)

# --- Owner settings --------------------------------------------------------
st.subheader("Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner.name = st.text_input("Owner name", value=owner.name)
with col_b:
    owner.minutes_available = st.number_input(
        "Minutes available today", min_value=1, max_value=600,
        value=owner.minutes_available,
    )

st.divider()

# --- Add a pet -------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed.strip()))
            save()
            st.success(f"Added {pet_name}.")
        else:
            st.warning("Please enter a pet name.")

st.divider()

# --- Add a task to a pet ---------------------------------------------------
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        target = st.selectbox("For which pet?", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col2:
            start_time = st.text_input("Time (HH:MM)", value="08:00")
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        if st.form_submit_button("Add task"):
            pet = owner.pets[pet_names.index(target)]
            pet.add_task(
                Task(
                    name=task_title.strip() or "Untitled task",
                    duration_min=int(duration),
                    priority=priority,
                    frequency=frequency,
                    time=start_time.strip(),
                )
            )
            save()
            st.success(f"Added '{task_title}' for {target} at {start_time}.")

# --- Current pets & tasks --------------------------------------------------
if owner.pets:
    st.markdown("### Your Pets")
    for p_idx, pet in enumerate(owner.pets):
        label = f"{pet.name} ({pet.species}" + (f", {pet.breed}" if pet.breed else "") + ")"
        with st.expander(label, expanded=True):
            if not pet.tasks:
                st.caption("No tasks yet.")
            for t_idx, task in enumerate(pet.tasks):
                c1, c2 = st.columns([5, 1])
                with c1:
                    status = "✅" if task.done else "—"
                    st.write(
                        f"{status} **{task.name}** · {task.time or '--:--'} · "
                        f"{task.duration_min} min · {task.priority} · {task.frequency}"
                    )
                with c2:
                    # Completing a recurring task auto-queues its next occurrence.
                    if not task.done and st.button("Done", key=f"done-{p_idx}-{t_idx}"):
                        upcoming = scheduler.complete_task(pet, task)
                        save()
                        if upcoming is not None:
                            st.toast(f"Next {task.name} queued for {upcoming.due_date}")
                        st.rerun()

st.divider()

# --- Build schedule --------------------------------------------------------
st.subheader("Today's Schedule")

# Conflict warnings surface first so the owner sees clashes before planning.
conflicts = scheduler.detect_conflicts()
for warning in conflicts:
    st.warning(f"⚠️ {warning}")

# Next-available-slot finder.
with st.expander("🕳️ Find the next free slot"):
    want = st.number_input("Task length (min)", min_value=5, max_value=240, value=30, step=5)
    if st.button("Find slot"):
        slot = scheduler.next_available_slot(int(want))
        if slot:
            st.info(f"Earliest free {want}-min slot today: **{slot}**")
        else:
            st.warning("No free slot that long left in the day (08:00–21:00).")

if st.button("Generate schedule"):
    plan = scheduler.build_plan()
    if not plan:
        st.info("No tasks to plan yet. Add some tasks above.")
    else:
        # Prioritized plan that fits the daily time budget.
        st.markdown("#### Prioritized plan (fits your time budget)")
        st.table(
            [
                {
                    "#": i,
                    "Time": task.time or "--:--",
                    "Task": task.name,
                    "Pet": pet.name,
                    "Min": task.duration_min,
                    "Priority": task.priority,
                }
                for i, (pet, task) in enumerate(plan, start=1)
            ]
        )
        st.success(scheduler.explain().replace("\n", "  \n"))

        # Full timeline, sorted chronologically by start time.
        st.markdown("#### Full day, sorted by time")
        st.table(
            [
                {"Time": t.time or "--:--", "Task": t.name, "Done": "✅" if t.done else "—"}
                for t in scheduler.sort_by_time()
            ]
        )
