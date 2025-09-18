import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import requests

# ------------------- Config -------------------
MANILA = ZoneInfo("Asia/Manila")
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

def send_discord_message(message: str):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Discord webhook error: {e}")

# ------------------- Intervals & Boss Names -------------------
intervals = {
    "Amentis": 1740, "General Aqulcus": 1740, "Baron Braudmore": 1920, "Gareth": 1920,
    "Shuliar": 2100, "Larba": 2100, "Catena": 2100, "Lady Dalia": 1080,
    "Titore": 2220, "Duplican": 2880, "Wannitas": 2880, "Metus": 2880,
    "Asta": 3720, "Ordo": 3720, "Secreta": 3720, "Supore": 3720,
}

next_times_str = [
    "2025-09-18 09:42 PM","2025-09-18 09:45 PM","2025-09-19 12:37 AM","2025-09-19 12:38 AM",
    "2025-09-19 03:49 AM","2025-09-19 03:55 AM","2025-09-19 04:12 AM","2025-09-19 05:58 AM",
    "2025-09-19 04:36 PM","2025-09-19 04:40 PM","2025-09-19 04:46 PM","2025-09-20 06:53 AM",
    "2025-09-20 06:59 AM","2025-09-20 07:07 AM","2025-09-20 07:15 AM",
]

boss_names = [
    "Amentis","General Aqulcus","Baron Braudmore","Gareth","Shuliar","Larba","Catena","Lady Dalia",
    "Titore","Duplican","Wannitas","Metus","Asta","Ordo","Secreta","Supore"
]

other_bosses = [
    ("Venatus", 600, "12:31 PM"),("Viorent", 600, "12:32 PM"),("Ego", 1260, "04:32 PM"),
    ("Araneo", 1440, "04:33 PM"),("Livera", 1440, "04:36 PM"),("Undomiel", 1440, "04:42 PM"),
]

# ------------------- Timer Class -------------------
class TimerEntry:
    def __init__(self, name, interval_minutes, last_time_str):
        self.name = name
        self.interval_minutes = interval_minutes
        self.interval = interval_minutes * 60
        try:
            parsed_time = datetime.strptime(last_time_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            today = datetime.now(tz=MANILA).date()
            parsed_time = datetime.strptime(f"{today} {last_time_str}", "%Y-%m-%d %I:%M %p")
        parsed_time = parsed_time.replace(tzinfo=MANILA)
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

    def countdown_color(self):
        seconds = self.countdown().total_seconds()
        if seconds < 60:
            return "red"
        elif seconds < 300:
            return "orange"
        else:
            return "green"

# ------------------- Build Timers -------------------
def build_timers():
    last_times_data = []
    for name, next_str in zip(boss_names, next_times_str):
        next_time = datetime.strptime(next_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=MANILA)
        interval_sec = intervals[name] * 60
        last_time = next_time - timedelta(seconds=interval_sec)
        last_times_data.append((name, intervals[name], last_time.strftime("%Y-%m-%d %I:%M %p")))
    timers_data = other_bosses + last_times_data
    return [TimerEntry(*data) for data in timers_data]

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Lord9 Santiago 7 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Santiago 7 Boss Timer")

st_autorefresh(interval=1000, key="refresh")

if "timers" not in st.session_state:
    st.session_state.timers = build_timers()
timers = st.session_state.timers

if "unique_timers" not in st.session_state:
    st.session_state.unique_timers = []

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

# ------------------- Build DataFrame -------------------
def build_df(timers_list):
    df = pd.DataFrame({
        "Name": [t.name for t in timers_list],
        "Interval (min)": [t.interval_minutes for t in timers_list],
        "Last Time": [t.last_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_list],
        "Countdown": [t.format_countdown() for t in timers_list],
        "Next Time": [t.next_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_list],
        "Status": ["Alive" if t.countdown().total_seconds() > 0 else "Killed" for t in timers_list],
        "Color": [t.countdown_color() for t in timers_list],
    })
    return df

# ------------------- Tabs Layout -------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "World Boss Spawn",
    "Manage & Edit Timers",
    "Unique Bosses Table",
    "Manage & Edit Unique Bosses"
])

# --- Tab 1: World Boss Spawn ---
with tab1:
    st.subheader("World Boss Spawn Table")
    df = build_df(timers)
    st.dataframe(
        df.drop(columns=["Color"])
          .style.apply(lambda s: [f"color: {c}" for c in df["Color"]], subset=["Countdown"], axis=0),
        height=300,
        use_container_width=True
    )

# --- Tab 2: Manage & Edit Official Timers ---
with tab2:
    st.subheader("Reset All Timers")
    if st.button("Reset All Timers"):
        now = datetime.now(tz=MANILA)
        for timer in timers:
            timer.last_time = now
            timer.next_time = now + timedelta(seconds=timer.interval)
            st.session_state[f"{timer.name}_5min"] = False
            st.session_state[f"{timer.name}_spawn"] = False
        send_discord_message(f"♻️ @everyone All boss timers have been reset manually at {now.strftime('%Y-%m-%d %I:%M %p')}.")
        st.success("All official timers reset!")

    st.subheader("Edit Timer Times (Pick Date & Time)")
    for timer in timers:
        with st.expander(f"Edit {timer.name}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                last_date = st.date_input("Select Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date")
                last_time = st.time_input("Select Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time")
                timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
            with col2:
                next_date = st.date_input("Select Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date")
                next_time = st.time_input("Select Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time")
                timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
            st.session_state[f"{timer.name}_5min"] = False
            st.session_state[f"{timer.name}_spawn"] = False

# --- Tab 3: Unique Bosses Table (Display Only) ---
with tab3:
    st.subheader("Unique Bosses Table")
    if st.session_state.unique_timers:
        df_unique = build_df(st.session_state.unique_timers)
        st.dataframe(
            df_unique.drop(columns=["Color"]),
            height=300,
            use_container_width=True
        )
    else:
        st.info("No Unique Bosses added yet.")

# --- Tab 4: Manage & Edit Unique Bosses ---
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
        st.subheader("Reset All Unique Bosses")
        if st.button("Reset All Unique Bosses"):
            now = datetime.now(tz=MANILA)
            for timer in st.session_state.unique_timers:
                timer.last_time = now
                timer.next_time = now + timedelta(seconds=timer.interval)
            st.success("✅ All Unique Bosses reset!")

        st.subheader("Edit Unique Bosses")
        for timer in st.session_state.unique_timers:
            with st.expander(f"Edit {timer.name}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    last_date = st.date_input("Select Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date_u")
                    last_time = st.time_input("Select Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time_u")
                    timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                with col2:
                    next_date = st.date_input("Select Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date_u")
                    next_time = st.time_input("Select Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time_u")
                    timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
