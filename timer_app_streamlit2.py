import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Manila timezone
TIMEZONE = ZoneInfo("Asia/Manila")

# ================= TimerEntry Class =================
class TimerEntry:
    def __init__(self, name, interval, last_time_str):
        self.name = name
        self.interval = int(interval)
        self.last_time = datetime.strptime(last_time_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=TIMEZONE)

    def next_spawn(self):
        return self.last_time + timedelta(minutes=self.interval)

    def countdown(self):
        return self.next_spawn() - datetime.now(TIMEZONE)

    def to_dict(self):
        return {
            "Boss Name": self.name,
            "Interval (min)": self.interval,
            "Time Killed": self.last_time.strftime("%Y-%m-%d %I:%M %p"),
            "Countdown": str(self.countdown()).split(".")[0],
            "Next Spawn": self.next_spawn().strftime("%Y-%m-%d %I:%M %p"),
        }

# ================= Initial Data =================
if "timers" not in st.session_state:
    st.session_state.timers = [
        TimerEntry("Venatus", 600, "2025-09-19 12:31 PM"),
        TimerEntry("Viorent", 600, "2025-09-19 12:32 PM"),
        TimerEntry("Lady Dalia", 1080, "2025-09-19 05:58 AM"),
        TimerEntry("Amentis", 1740, "2025-09-18 09:42 PM"),
        TimerEntry("General Aqulcus", 1740, "2025-09-18 09:45 PM"),
        TimerEntry("Metus", 2880, "2025-09-18 06:53 AM"),
        TimerEntry("Asta", 3720, "2025-09-17 04:59 PM"),
        TimerEntry("Ordo", 3720, "2025-09-17 05:07 PM"),
        TimerEntry("Secreta", 3720, "2025-09-17 05:15 PM"),
        TimerEntry("Baron Braudmore", 1920, "2025-09-19 12:37 AM"),
        TimerEntry("Gareth", 1920, "2025-09-19 12:38 AM"),
        TimerEntry("Ego", 1260, "2025-09-19 04:32 PM"),
        TimerEntry("Shuliar", 2100, "2025-09-19 03:49 AM"),
        TimerEntry("Larba", 2100, "2025-09-19 03:55 AM"),
        TimerEntry("Catena", 2100, "2025-09-19 04:12 AM"),
        TimerEntry("Araneo", 1440, "2025-09-19 04:33 PM"),
        TimerEntry("Livera", 1440, "2025-09-19 04:36 PM"),
        TimerEntry("Undomiel", 1440, "2025-09-19 04:42 PM"),
        TimerEntry("Titore", 2220, "2025-09-19 04:36 PM"),
        TimerEntry("Duplican", 2880, "2025-09-19 04:40 PM"),
        TimerEntry("Wannitas", 2880, "2025-09-19 04:46 PM"),
    ]

if "unique_timers" not in st.session_state:
    st.session_state.unique_timers = []

# ================= Helper Functions =================
def timers_to_df(timers_list):
    return pd.DataFrame([t.to_dict() for t in timers_list])

def render_table(timers_list):
    df = timers_to_df(timers_list)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ================= Tabs =================
tabs = st.tabs(["World Boss Spawn", "Manage & Edit Timers",
                "Unique Boss Spawn", "Manage & Edit Unique Bosses"])

# Tab 1: World Boss Spawn
with tabs[0]:
    st.header("World Boss Spawn")
    render_table(st.session_state.timers)

# Tab 2: Manage & Edit Timers
with tabs[1]:
    st.header("Manage & Edit Timers")
    for i, timer in enumerate(st.session_state.timers):
        with st.expander(f"Edit {timer.name}"):
            new_last_time = st.text_input(
                f"Enter new Last Time for {timer.name} (YYYY-MM-DD HH:MM AM/PM)",
                value=timer.last_time.strftime("%Y-%m-%d %I:%M %p"),
                key=f"last_time_{i}"
            )
            if st.button(f"Save {timer.name}", key=f"save_{i}"):
                try:
                    st.session_state.timers[i].last_time = datetime.strptime(new_last_time, "%Y-%m-%d %I:%M %p").replace(tzinfo=TIMEZONE)
                    st.success(f"{timer.name} updated successfully!")
                except ValueError:
                    st.error("Invalid time format. Use YYYY-MM-DD HH:MM AM/PM")

# Tab 3: Unique Boss Spawn
with tabs[2]:
    st.header("Unique Boss Spawn")
    if st.session_state.unique_timers:
        render_table(st.session_state.unique_timers)
    else:
        st.info("No unique bosses added yet.")

# Tab 4: Manage & Edit Unique Bosses
with tabs[3]:
    st.header("Manage & Edit Unique Bosses")
    with st.form("add_unique_boss"):
        name = st.text_input("Boss Name")
        interval = st.number_input("Interval (minutes)", min_value=1, step=1)
        last_time = st.text_input("Last Time (YYYY-MM-DD HH:MM AM/PM)", value=datetime.now(TIMEZONE).strftime("%Y-%m-%d %I:%M %p"))
        submitted = st.form_submit_button("Add Unique Boss")
        if submitted:
            try:
                new_boss = TimerEntry(name, interval, last_time)
                st.session_state.unique_timers.append(new_boss)
                st.success(f"Added unique boss: {name}")
            except ValueError:
                st.error("Invalid time format. Use YYYY-MM-DD HH:MM AM/PM")

    st.subheader("Edit Unique Bosses")
    for i, timer in enumerate(st.session_state.unique_timers):
        with st.expander(f"Edit {timer.name}"):
            new_last_time = st.text_input(
                f"Enter new Last Time for {timer.name} (YYYY-MM-DD HH:MM AM/PM)",
                value=timer.last_time.strftime("%Y-%m-%d %I:%M %p"),
                key=f"unique_last_time_{i}"
            )
            if st.button(f"Save {timer.name}", key=f"unique_save_{i}"):
                try:
                    st.session_state.unique_timers[i].last_time = datetime.strptime(new_last_time, "%Y-%m-%d %I:%M %p").replace(tzinfo=TIMEZONE)
                    st.success(f"{timer.name} updated successfully!")
                except ValueError:
                    st.error("Invalid time format. Use YYYY-MM-DD HH:MM AM/PM")

    if st.button("Reset All Unique Bosses"):
        st.session_state.unique_timers = []
        st.warning("All unique bosses have been reset!")
