# Lord9 Boss Timer Streamlit app with Discord notifications

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import requests

# Manila timezone
MANILA = ZoneInfo("Asia/Manila")

# Discord webhook URL (replace with your webhook)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1418197835563794532/M7pM6nDxLWNw5dzCC6DNQABpiQxlS-hojqFVlZDHSLZ_MIt_efPt2qx1qqzd1O9Zw2Z8"

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

# Next times provided by user
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

# Merge all timers
timers_data = other_bosses + last_times_data

# ---------------- TimerEntry Class ----------------
class TimerEntry:
    def __init__(self, name, interval_minutes, last_time_str):
        self.name = name
        self.interval_minutes = interval_minutes
        self.interval = interval_minutes * 60
        self.notified = False
        self.pre_notified = False  # 5-min pre-warning

        # ---------------- Fixed parsing ----------------
        try:
            # Try full date first
            parsed_time = datetime.strptime(last_time_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            # If no date, assume today
            today_str = datetime.now(tz=MANILA).strftime("%Y-%m-%d")
            parsed_time = datetime.strptime(f"{today_str} {last_time_str}", "%Y-%m-%d %I:%M %p")
        parsed_time = parsed_time.replace(tzinfo=MANILA)
        self.last_time = parsed_time
        self.next_time = self.last_time + timedelta(seconds=self.interval)
        self.update_next()

    def update_next(self):
        now = datetime.now(tz=MANILA)
        seconds_passed = (now - self.last_time).total_seconds()
        intervals_passed = max(0, int(seconds_passed // self.interval))
        self.last_time = self.last_time + timedelta(seconds=self.interval * intervals_passed)
        self.next_time = self.last_time + timedelta(seconds=self.interval)
        if self.notified and now < self.next_time:
            self.notified = False
        if self.pre_notified and now < self.next_time - timedelta(minutes=5):
            self.pre_notified = False

    def countdown(self):
        return self.next_time - datetime.now(tz=MANILA)

    def format_countdown(self):
        td = self.countdown()
        total_seconds = int(td.total_seconds())
        if total_seconds < 0:
            return "00:00:00"
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
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

    def check_spawn_notify(self):
        now = datetime.now(tz=MANILA)
        # 5-minute pre-spawn
        if not self.pre_notified and now >= self.next_time - timedelta(minutes=5):
            self.send_discord_notification(pre_spawn=True)
            self.pre_notified = True
        # Actual spawn
        if not self.notified and now >= self.next_time:
            self.send_discord_notification(pre_spawn=False)
            self.notified = True

    def send_discord_notification(self, pre_spawn=False):
        countdown_str = self.format_countdown()
        if pre_spawn:
            content = f"@everyone ⚔️ **{self.name}** will spawn in 5 minutes! Countdown: {countdown_str} (Time: {self.next_time.strftime('%I:%M %p')})"
        else:
            content = f"@everyone ⚔️ **{self.name}** has spawned! Time: {self.next_time.strftime('%I:%M %p')}"
        data = {"content": content}
        try:
            requests.post(DISCORD_WEBHOOK_URL, json=data)
        except Exception as e:
            print("Discord notification failed:", e)

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Lord9 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Boss Timer (Manila Time GMT+8)")

# Auto-refresh every second
st_autorefresh(interval=1000, key="refresh")

# Initialize timers
timers = [TimerEntry(*data) for data in timers_data]

# Update timers and send notifications
for t in timers:
    t.update_next()
    t.check_spawn_notify()

# Sort by next spawn
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

# ---------------- requirements.txt ----------------
# streamlit
# pandas
# streamlit-autorefresh
# requests
