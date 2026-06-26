import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care based on time and priority.")

# --- Application memory ----------------------------------------------------
# Streamlit re-runs this script top-to-bottom on every interaction, so we keep
# the Owner (and all its pets/tasks) in st.session_state instead of recreating
# it each run. Create it once, then reuse the persisted instance.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", minutes_available=60)

owner: Owner = st.session_state.owner

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
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col3:
            frequency = st.selectbox("Frequency", ["daily", "weekly"])
        if st.form_submit_button("Add task"):
            pet = owner.pets[pet_names.index(target)]
            pet.add_task(
                Task(
                    name=task_title.strip() or "Untitled task",
                    duration_min=int(duration),
                    priority=priority,
                    frequency=frequency,
                )
            )
            st.success(f"Added '{task_title}' for {target}.")

# --- Current pets & tasks --------------------------------------------------
if owner.pets:
    st.markdown("### Your Pets")
    for pet in owner.pets:
        label = f"{pet.name} ({pet.species}" + (f", {pet.breed}" if pet.breed else "") + ")"
        with st.expander(label, expanded=True):
            if pet.tasks:
                st.table(
                    [
                        {
                            "Task": t.name,
                            "Duration (min)": t.duration_min,
                            "Priority": t.priority,
                            "Frequency": t.frequency,
                            "Done": "✅" if t.done else "—",
                        }
                        for t in pet.tasks
                    ]
                )
            else:
                st.caption("No tasks yet.")

st.divider()

# --- Build schedule --------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()
    if not plan:
        st.warning("No tasks to plan. Add some tasks above.")
    else:
        st.markdown("#### Today's Schedule")
        for i, (pet, task) in enumerate(plan, start=1):
            st.write(
                f"**{i}. {task.name}** for {pet.name} — "
                f"{task.duration_min} min · priority: {task.priority}"
            )
        st.info(scheduler.explain())
