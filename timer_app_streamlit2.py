import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# Manila timezone
TIMEZONE = ZoneInfo("Asia/Manila")

# Auto refresh every 1 second
st_autorefresh(interval=1000, key="refresh")

# === Timer Class ===
class TimerEntry:
    def __init__(self, name, interval, last_time):
        self.name = name
        self.interval = interval  # minutes
        self.last_time = datetime.strptime(last_time, "%Y-%m-%d %I:%M %p").replace(tzinfo=TIMEZONE)

    def next_time(self):
        return self.last_time + timedelta(minutes=self.interval)

    def countdown(self):
        return self.next_time() - datetime.now(TIMEZONE)

# === Initial Boss Data ===
initial_data = [
    ("Venatus", 600, "2025-09-19 12:31 PM"),
    ("Viorent", 600, "2025-09-19 12:32 PM"),
    ("Lady Dalia", 1080, "2025-09-19 05:58 AM"),
    ("Amentis", 1740, "2025-09-18 09:42 PM"),
    ("General Aqulcus", 1740, "2025-09-18 09:45 PM"),
    ("Metus", 2880, "2025-09-18 06:53 AM"),
    ("Asta", 3720, "2025-09-17 04:59 PM"),
    ("Ordo", 3720, "2025-09-17 05:07 PM"),
    ("Secreta", 3720, "2025-09-17 05:15 PM"),
    ("Baron Braudmore", 1920, "2025-09-19 12:37 AM"),
    ("Gareth", 1920, "2025-09-19 12:38 AM"),
    ("Ego", 1260, "2025-09-19 04:32 PM"),
    ("Shuliar", 2100, "2025-09-19 03:49 AM"),
    ("Larba", 2100, "2025-09-19 03:55 AM"),
    ("Catena", 2100, "2025-09-19 04:12 AM"),
    ("Araneo", 1440, "2025-09-19 04:33 PM"),
    ("Livera", 1440, "2025-09-19 04:36 PM"),
    ("Undomiel", 1440, "2025-09-19 04:42 PM"),
    ("Titore", 2220, "2025-09-19 04:36 PM"),
    ("Duplican", 2880, "2025-09-19 04:40 PM"),
    ("Wannitas", 2880, "2025-09-19 04:46 PM"),
]

# === Session State Initialization ===
if "timers" not in st.session_state:
    st.session_state.timers = [TimerEntry(*data) for data in initial_data]

if "unique_bosses" not in st.session_state:
    st.session_state.unique_bosses = []

# === Helper Functions ===
def timers_to_df(timers):
    rows = []
    for t in timers:
        rows.append({
            "Boss Name": t.name,
            "Interval (min)": t.interval,
            "Last Time": t.last_time.strftime("%Y-%m-%d %I:%M %p"),
            "Countdown": str(t.countdown()).split(".")[0],
            "Next Spawn": t.next_time().strftime("%Y-%m-%d %I:%M %p")
        })
    return pd.DataFrame(rows)

def next_boss_banner(timers_list):
    if not timers_list:
        return
    next_timer = min(timers_list, key=lambda x: x.countdown())
    st.markdown(
        f"### ⏰ Next Boss: **{next_timer.name}** at {next_timer.next_time().strftime('%Y-%m-%d %I:%M %p')} "
        f"({str(next_timer.countdown()).split('.')[0]} left)"
    )

# === Tabs ===
tab1, tab2, tab3, tab4 = st.tabs([
    "World Boss Spawn",
    "Manage/Edit Timers",
    "Unique Bosses",
    "Manage Unique Bosses"
])

# === Tab 1: World Boss Spawn ===
with tab1:
    st.title("🌍 World Boss Spawn (Manila Time GMT+8)")
    timers_df = timers_to_df(st.session_state.timers)
    st.dataframe(timers_df, use_container_width=True, hide_index=True)
    next_boss_banner(st.session_state.timers)

# === Tab 2: Manage/Edit Timers ===
with tab2:
    st.header("⚙️ Manage and Edit Timers")

    edited_last_times = {}
    for timer in st.session_state.timers:
        col1, col2 = st.columns([2, 2])
        with col1:
            st.write(f"**{timer.name}**")
        with col2:
            edited_time = st.text_input(
                f"Last Time for {timer.name}",
                timer.last_time.strftime("%Y-%m-%d %I:%M %p"),
                key=f"last_{timer.name}"
            )
            edited_last_times[timer.name] = edited_time

    if st.button("💾 Save Changes"):
        for timer in st.session_state.timers:
            new_last = edited_last_times[timer.name]
            try:
                timer.last_time = datetime.strptime(new_last, "%Y-%m-%d %I:%M %p").replace(tzinfo=TIMEZONE)
            except ValueError:
                st.error(f"Invalid date format for {timer.name}. Use YYYY-MM-DD HH:MM AM/PM")

    if st.button("♻️ Reset All Timers"):
        now = datetime.now(TIMEZONE)
        for timer in st.session_state.timers:
            timer.last_time = now

# === Tab 3: Unique Bosses (Spawn Table) ===
with tab3:
    st.header("⭐ Unique Bosses (Manual Input)")
    unique_df = timers_to_df(st.session_state.unique_bosses)
    if not unique_df.empty:
        st.dataframe(unique_df, use_container_width=True, hide_index=True)
        next_boss_banner(st.session_state.unique_bosses)
    else:
        st.info("No Unique Bosses added yet.")

# === Tab 4: Manage Unique Bosses ===
with tab4:
    st.header("⚙️ Manage Unique Bosses")

    if st.button("➕ Add Unique Boss"):
        st.session_state.unique_bosses.append(
            TimerEntry("New Boss", 60, datetime.now(TIMEZONE).strftime("%Y-%m-%d %I:%M %p"))
        )

    edited_unique_last = {}
    edited_unique_interval = {}
    for idx, timer in enumerate(st.session_state.unique_bosses):
        st.write(f"**{timer.name}**")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            new_name = st.text_input("Name", timer.name, key=f"uname_{idx}")
        with col2:
            new_interval = st.number_input("Interval (min)", value=timer.interval, key=f"uinterval_{idx}")
            edited_unique_interval[idx] = new_interval
        with col3:
            new_last_time = st.text_input(
                "Last Time", timer.last_time.strftime("%Y-%m-%d %I:%M %p"), key=f"ulast_{idx}"
            )
            edited_unique_last[idx] = new_last_time
        timer.name = new_name

    if st.button("💾 Save Unique Boss Changes"):
        for idx, timer in enumerate(st.session_state.unique_bosses):
            try:
                timer.last_time = datetime.strptime(
                    edited_unique_last[idx], "%Y-%m-%d %I:%M %p"
                ).replace(tzinfo=TIMEZONE)
                timer.interval = edited_unique_interval[idx]
            except ValueError:
                st.error(f"Invalid date format for {timer.name}. Use YYYY-MM-DD HH:MM AM/PM")

    if st.button("♻️ Reset All Unique Bosses"):
        now = datetime.now(TIMEZONE)
        for timer in st.session_state.unique_bosses:
            timer.last_time = now
