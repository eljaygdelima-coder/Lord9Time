# Repo-ready Streamlit app for Lord9 Boss Timer with Last Times calculated from Next Times and fixed datetime parsing

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
from streamlit_autorefresh import st_autorefresh

# Manila timezone
MANILA = ZoneInfo("Asia/Manila")

# Intervals in minutes
intervals = {
    "Amentis": 1740,
    "General Aqulcus": 1740,
    "Baron Braudmore": 1920,
    "Gareth": 1920,
    "Shuliar": 2100,
    "Larba": 2100,
    "Catena": 2100,
    "Lady Dalia": 1080,
    "Titore": 2220,
    "Duplican": 2880,
    "Wannitas": 2880,
    "Metus": 2880,
    "Asta": 3720,
    "Ordo": 3720,
    "Secreta": 3720,
    "Supore": 3720,
}

# Next times you provided
next_times_str = [
    "2025-09-18 09:42 PM",
    "2025-09-18 09:45 PM",
    "2025-09-19 12:37 AM",
    "2025-09-19 12:38 AM",
    "2025-09-19 03:49 AM",
    "2025-09-19 03:55 AM",
    "2025-09-19 04:12 AM",
    "2025-09-19 05:58 AM",
    "2025-09-19 04:36 PM",
    "2025-09-19 04:40 PM",
    "2025-09-19 04:46 PM",
    "2025-09-20 06:53 AM",
    "2025-09-20 06:59 AM",
    "2025-09-20 07:07 AM",
    "2025-09-20 07:15 AM",
]

boss_names = [
    "Amentis", "General Aqulcus", "Baron Braudmore", "Gareth", "Shuliar", "Larba", "Catena", "Lady Dalia",
    "Titore", "Duplican", "Wannitas", "Metus", "Asta", "Ordo", "Secreta", "Supore"
]

# Compute Last Times based on Next Time minus interval
last_times_data = []
for name, next_str in zip(boss_names, next_times_str):
    next_time = datetime.strptime(next_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=MANILA)
    interval_sec = intervals[name] * 60
    last_time = next_time - timedelta(seconds=interval_sec)
    last_times_data.append((name, intervals[name], last_time.strftime("%Y-%m-%d %I:%M %p")))

# Other bosses unchanged
other_bosses = [
    ("Venatus", 600, "12:31 PM"),
    ("Viorent", 600, "12:32 PM"),
    ("Ego", 1260, "04:32 PM"),
    ("Araneo", 1440, "04:33 PM"),
    ("Livera", 1440, "04:36 PM"),
    ("Undomiel", 1440, "04:42 PM"),
]

# Merge all timers data
timers_data = other_bosses + last_times_data

class TimerEntry:
    def __init__(self, name, interval_minutes, last_time_str):
        self.name = name
        self.interval_minutes = interval_minutes
        self.interval = interval_minutes * 60

        # Fixed parsing to handle both full datetime and time-only strings
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

st.set_page_config(page_title="Lord9 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Boss Timer (Manila Time GMT+8)")
st_autorefresh(interval=1000, key="refresh")

# Initialize timers
timers = [TimerEntry(*data) for data in timers_data]
for t in timers:
    t.update_next()

# Sort timers by next spawn
timers_sorted = sorted(timers, key=lambda x: x.countdown())

# Build DataFrame
df = pd.DataFrame({
    "Name": [t.name for t in timers_sorted],
    "Interval (min)": [t.interval_minutes for t in timers_sorted],
    "Last Time": [t.last_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_sorted],
    "Countdown": [t.format_countdown() for t in timers_sorted],
    "Next Time": [t.next_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_sorted],
    "Color": [t.countdown_color() for t in timers_sorted],
})

def color_countdown(s):
    return [f"color: {c}" for c in df["Color"]]

st.dataframe(df.drop(columns=["Color"]).style.apply(color_countdown, subset=["Countdown"], axis=0))

# requirements.txt contents:
# streamlit
# pandas
# streamlit-autorefresh
