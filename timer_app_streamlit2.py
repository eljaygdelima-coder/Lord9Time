import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# ------------------- Config -------------------
MANILA = ZoneInfo("Asia/Manila")

# ------------------- Boss Data -------------------
boss_data = [
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

# ------------------- Timer Class -------------------
class TimerEntry:
    def __init__(self, name, interval_minutes, last_time_str):
        self.name = name
        self.interval_minutes = interval_minutes
        self.interval = interval_minutes * 60
        self.last_time = datetime.strptime(last_time_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=MANILA)
        self.next_time = self.last_time + timedelta(seconds=self.interval)
        self.update_next()

    def update_next(self):
        now = datetime.now(tz=MANILA)
        while self.next_time < now:
            self.last_time = self.next_time
            self.next_time = self.last_time + timedelta(seconds=self.interval)

    def countdown(self):
        return self.next_time - datetime.now(tz=MANILA)

    def format_countdown(self):
        td = self.countdown()
        total_seconds = int(td.total_seconds())
        if total_seconds < 0:
            return "00:00:00"
        days, rem = divmod(total_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if days > 0:
            return f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
        return f"{hours:02}:{minutes:02}:{seconds:02}"

# ------------------- Build Timers -------------------
def build_timers():
    return [TimerEntry(*data) for data in boss_data]

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Lord9 Santiago 7 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Santiago 7 Boss Timer")
st_autorefresh(interval=1000, key="timer_refresh")  # refresh every 1 sec

if "timers" not in st.session_state:
    st.session_state.timers = build_timers()
if "unique_timers" not in st.session_state:
    st.session_state.unique_timers = []

timers = st.session_state.timers

# ------------------- Next Boss Banner -------------------
def next_boss_banner(timers_list):
    for t in timers_list:
        t.update_next()
    if not timers_list:
        return
    next_timer = min(timers_list, key=lambda x: x.countdown())
    remaining = next_timer.countdown().total_seconds()
    if remaining <= 60:
        cd_color = "red"
    elif remaining <= 300:
        cd_color = "orange"
    else:
        cd_color = "green"
    st.markdown(
        f"<h2 style='text-align:center'>Next Boss: {next_timer.name} | "
        f"Spawn: {next_timer.next_time.strftime('%Y-%m-%d %I:%M %p')} | "
        f"<span style='color:{cd_color}'>{next_timer.format_countdown()}</span></h2>",
        unsafe_allow_html=True
    )

next_boss_banner(timers)

# ------------------- Interactive Table -------------------
def display_boss_table_interactive(timers_list):
    for t in timers_list:
        t.update_next()
    
    data = {
        "Boss Name": [t.name for t in timers_list],
        "Interval (min)": [t.interval_minutes for t in timers_list],
        "Time Killed": [t.last_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_list],
        "Countdown": [t.format_countdown() for t in timers_list],
        "Next Spawn": [t.next_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_list],
    }
    df = pd.DataFrame(data)

    # Color coding countdown
    def color_countdown(val):
        timer = next((x for x in timers_list if x.format_countdown() == val), None)
        if timer:
            remaining = timer.countdown().total_seconds()
            if remaining <= 60:
                return 'color: red'
            elif remaining <= 300:
                return 'color: orange'
            else:
                return 'color: green'
        return ''
    
    st.dataframe(df.style.applymap(color_countdown, subset=['Countdown']))

# ------------------- Tabs -------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "World Boss Spawn",
    "Manage & Edit Timers",
    "Unique Bosses Table",
    "Manage & Edit Unique Bosses"
])

with tab1:
    st.subheader("World Boss Spawn Table")
    display_boss_table_interactive(timers)

with tab2:
    st.subheader("Edit Timer Times (Pick Date & Time)")
    for timer in timers:
        with st.expander(f"Edit {timer.name}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                last_date = st.date_input("Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date")
                last_time = st.time_input("Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time")
            with col2:
                next_date = st.date_input("Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date")
                next_time = st.time_input("Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time")
            if st.button(f"💾 Save {timer.name}", key=f"save_{timer.name}"):
                timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
                st.success(f"{timer.name} updated successfully!")

with tab3:
    st.subheader("Unique Bosses Table")
    if st.session_state.unique_timers:
        display_boss_table_interactive(st.session_state.unique_timers)
    else:
        st.info("No Unique Bosses added yet.")

with tab4:
    st.subheader("Add Unique Boss")
    new_name = st.text_input("Boss Name", key="unique_name")
    new_interval = st.number_input("Interval (minutes)", min_value=1, value=60, step=1, key="unique_interval")
    col1, col2 = st.columns(2)
    with col1:
        new_last_date = st.date_input("Last Time Date", key="unique_last_date")
        new_last_time = st.time_input("Last Time", key="unique_last_time")
    with col2:
        new_next_date = st.date_input("Next Time Date", key="unique_next_date")
        new_next_time = st.time_input("Next Time", key="unique_next_time")

    if st.button("Add Unique Boss"):
        last_dt = datetime.combine(new_last_date, new_last_time).replace(tzinfo=MANILA)
        next_dt = datetime.combine(new_next_date, new_next_time).replace(tzinfo=MANILA)
        new_timer = TimerEntry(new_name, new_interval, last_dt.strftime("%Y-%m-%d %I:%M %p"))
        new_timer.next_time = next_dt
        st.session_state.unique_timers.append(new_timer)
        st.success(f"✅ Boss '{new_name}' added successfully!")

    if st.session_state.unique_timers:
        st.subheader("Edit Unique Bosses")
        for timer in st.session_state.unique_timers:
            with st.expander(f"Edit {timer.name}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    last_date = st.date_input("Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date_u")
                    last_time = st.time_input("Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time_u")
                with col2:
                    next_date = st.date_input("Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date_u")
                    next_time = st.time_input("Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time_u")
                if st.button(f"💾 Save {timer.name}", key=f"save_unique_{timer.name}"):
                    timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                    timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
                    st.success(f"{timer.name} updated successfully!")
