import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import requests
import pandas as pd

# ------------------- Config -------------------
MANILA = ZoneInfo("Asia/Manila")
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

def send_discord_message(message: str):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Discord webhook error: {e}")

# ------------------- Timer Class -------------------
class TimerEntry:
    def __init__(self, name, interval_minutes, last_time_str):
        self.name = name
        self.interval_minutes = interval_minutes
        self.interval = interval_minutes * 60
        parsed_time = datetime.strptime(last_time_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=MANILA)
        self.last_time = parsed_time
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

# ------------------- Default Boss Data -------------------
default_bosses = [
    ("Amentis", 1740, "2025-09-18 09:42 PM"),
    ("General Aqulcus", 1740, "2025-09-18 09:45 PM"),
    ("Baron Braudmore", 1920, "2025-09-19 12:37 AM"),
    ("Gareth", 1920, "2025-09-19 12:38 AM"),
    ("Shuliar", 2100, "2025-09-19 03:49 AM"),
    ("Larba", 2100, "2025-09-19 03:55 AM"),
    ("Catena", 2100, "2025-09-19 04:12 AM"),
    ("Lady Dalia", 1080, "2025-09-19 05:58 AM"),
    ("Titore", 2220, "2025-09-19 04:36 PM"),
    ("Duplican", 2880, "2025-09-19 04:40 PM"),
    ("Wannitas", 2880, "2025-09-19 04:46 PM"),
    ("Metus", 2880, "2025-09-20 06:53 AM"),
    ("Asta", 3720, "2025-09-20 06:59 AM"),
    ("Ordo", 3720, "2025-09-20 07:07 AM"),
    ("Secreta", 3720, "2025-09-20 07:15 AM"),
    ("Supore", 3720, "2025-09-20 07:30 AM"),
    ("Venatus", 600, "2025-09-18 12:31 PM"),
    ("Viorent", 600, "2025-09-18 12:32 PM"),
    ("Ego", 1260, "2025-09-18 04:32 PM"),
    ("Araneo", 1440, "2025-09-18 04:33 PM"),
    ("Livera", 1440, "2025-09-18 04:36 PM"),
    ("Undomiel", 1440, "2025-09-18 04:42 PM"),
]

# ------------------- Build Timers -------------------
def build_timers():
    return [TimerEntry(*data) for data in default_bosses]

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Lord9 Santiago 7 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Santiago 7 Boss Timer")
st_autorefresh(interval=1000, key="timer_refresh")

if "timers" not in st.session_state:
    st.session_state.timers = build_timers()
timers = st.session_state.timers

# ------------------- Discord Flags -------------------
for t in timers:
    if f"{t.name}_5min" not in st.session_state:
        st.session_state[f"{t.name}_5min"] = False
    if f"{t.name}_spawn" not in st.session_state:
        st.session_state[f"{t.name}_spawn"] = False

# ------------------- Discord Notifications -------------------
for t in timers:
    t.update_next()
    remaining = t.countdown().total_seconds()
    if 0 < remaining <= 300 and not st.session_state[f"{t.name}_5min"]:
        send_discord_message(f"⏰ @everyone {t.name} will spawn in 5 minutes! Next: {t.next_time.strftime('%Y-%m-%d %I:%M %p')}")
        st.session_state[f"{t.name}_5min"] = True
    if remaining <= 0 and not st.session_state[f"{t.name}_spawn"]:
        send_discord_message(f"⚔️ @everyone {t.name} has spawned! Next: {t.next_time.strftime('%Y-%m-%d %I:%M %p')}")
        st.session_state[f"{t.name}_spawn"] = True

# ------------------- Next Boss Banner -------------------
def next_boss_banner(timers_list):
    for t in timers_list:
        t.update_next()
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
    st.dataframe(df)

# ------------------- Tabs -------------------
tab1, tab2 = st.tabs([
    "World Boss Spawn",
    "Manage & Edit Timers"
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
                last_date = st.date_input("Select Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date")
                last_time = st.time_input("Select Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time")
            with col2:
                next_date = st.date_input("Select Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date")
                next_time = st.time_input("Select Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time")
            if st.button(f"Save {timer.name}", key=f"{timer.name}_save"):
                timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
                st.session_state[f"{timer.name}_5min"] = False
                st.session_state[f"{timer.name}_spawn"] = False
                st.success(f"{timer.name} updated successfully!")
