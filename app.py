import streamlit as st
import requests

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+ RPG", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ : Pet Care RPG")
st.caption("Manage your pets, level them up, and keep their stats high!")

# --- Application memory & persistence --------------------------------------
DATA_FILE = "data.json"
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE) or Owner(
        name="Player", minutes_available=120
    )

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def save() -> None:
    """Persist the current owner (and all nested data) to disk."""
    owner.save_to_json(DATA_FILE)


def get_pet_image(species: str) -> str:
    """Fetch a random pet image from public APIs."""
    try:
        if species.lower() == "dog":
            return requests.get("https://dog.ceo/api/breeds/image/random").json().get("message", "https://place.dog/300/300")
        elif species.lower() == "cat":
            return "https://cataas.com/cat"
    except:
        pass
    return "https://via.placeholder.com/300?text=Pet+Image"


# --- Sidebar: Owner & Pet Management ---------------------------------------
with st.sidebar:
    st.header("👤 Player Profile")
    owner.name = st.text_input("Name", value=owner.name)
    owner.minutes_available = st.number_input(
        "Daily Energy (Minutes)", min_value=1, max_value=600, value=owner.minutes_available
    )
    
    st.divider()
    st.subheader("➕ Summon a New Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        breed = st.text_input("Breed / Class")
        age = st.number_input("Age", min_value=0, max_value=50, value=1)
        if st.form_submit_button("Summon Pet"):
            if pet_name.strip():
                new_pet = Pet(name=pet_name.strip(), species=species, breed=breed.strip(), age=age)
                owner.add_pet(new_pet)
                save()
                st.success(f"{pet_name} joined your party!")
            else:
                st.warning("Please enter a pet name.")

# --- Main Area: RPG Pet Dashboards -----------------------------------------
st.header("🛡️ Your Party")
if not owner.pets:
    st.info("No pets in your party yet. Summon one from the sidebar!")

for p_idx, pet in enumerate(owner.pets):
    with st.container(border=True):
        col_img, col_stats, col_tasks = st.columns([1, 2, 2])
        
        with col_img:
            # RPG Avatar
            st.image(get_pet_image(pet.species), use_container_width=True)
            st.markdown(f"**{pet.name}**")
            st.caption(f"Lvl {pet.level} {pet.breed or pet.species.capitalize()} • Age: {pet.age}")

        with col_stats:
            # RPG Stats
            st.subheader("Stats")
            st.progress(pet.xp_progress(), text=f"XP: {pet.xp} / {pet.xp_to_next()}")
            
            c1, c2 = st.columns(2)
            c1.metric(label="❤️ Health", value=pet.health.capitalize())
            c2.metric(label="✨ Mood", value=pet.mood.capitalize())
            
            # --- New Attributes Section ---
            st.markdown("**Attributes**")
            c3, c4, c5 = st.columns(3)
            c3.metric(label="💨 Speed", value=pet.speed)
            c4.metric(label="🛡️ Endurance", value=pet.endurance)
            c5.metric(label="🧠 Intel", value=pet.intelligence)
            
            # Form to add tasks to this specific pet
            with st.popover(f"📝 Assign Quest (Task) to {pet.name}"):
                with st.form(f"task_form_{p_idx}", clear_on_submit=True):
                    t_name = st.text_input("Quest Name")
                    t_dur = st.number_input("Duration (min)", min_value=1, value=15)
                    t_pri = st.selectbox("Priority", ["low", "medium", "high"], index=1)
                    t_time = st.time_input("Start Time")
                    t_freq = st.selectbox("Frequency", ["daily", "weekly", "once"])
                    if st.form_submit_button("Assign"):
                        pet.add_task(Task(
                            name=t_name, duration_min=int(t_dur), priority=t_pri, 
                            frequency=t_freq, time=t_time.strftime("%H:%M")
                        ))
                        save()
                        st.rerun()

        with col_tasks:
            # Quest Log (Tasks)
            st.subheader("📜 Active Quests")
            if not pet.tasks:
                st.caption("No active quests.")
            for t_idx, task in enumerate(pet.tasks):
                if not task.done:
                    c_info, c_btn = st.columns([3, 1])
                    c_info.write(f"**{task.name}** \n⏰ {task.time or 'Anytime'} • ⏳ {task.duration_min}m • ⚠️ {task.priority.upper()}")
                    if c_btn.button("Complete", key=f"done_{p_idx}_{t_idx}"):
                        # Gamify completion: Grant XP based on task duration
                        xp_gained = task.duration_min * 10
                        leveled_up = pet.add_xp(xp_gained)
                        
                        upcoming = scheduler.complete_task(pet, task)
                        save()
                        
                        st.toast(f"Gained {xp_gained} XP!")
                        if leveled_up:
                            st.balloons()
                            st.toast(f"{pet.name} leveled up to Level {pet.level}! 🎉")
                        st.rerun()

st.divider()

# --- Calendar & Schedule Visualization -------------------------------------
st.header("📅 Daily Timetable")

# Show conflict warnings first
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.error(f"⚔️ Scheduling Conflict: {warning}")

plan = scheduler.build_plan()
if plan:
    st.success(scheduler.explain())
    
    # Visualizing as a simple timetable using Streamlit's DataFrame
    st.markdown("### 🕒 Timeline")
    timeline_data = []
    for pet, task in plan:
        timeline_data.append({
            "Time": task.time or "Flex",
            "Quest": task.name,
            "Party Member": pet.name,
            "Cost (Energy)": f"{task.duration_min} min",
            "Priority": task.priority.capitalize()
        })
        
    st.dataframe(timeline_data, use_container_width=True, hide_index=True)
else:
    st.info("No quests planned for today. Rest and recover your energy!")