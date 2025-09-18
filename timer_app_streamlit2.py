# Lord9 Santiago 7 Boss Timer Streamlit App with Discord Notifications, Reset, and Editable Times

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import requests

# ------------------- Configuration -------------------
MANILA = ZoneInfo("Asia/Manila")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1418231894214185010/FdUk0L07z-IJ8IIkhiyXNc6tejfrCeY2Svy-IPRpNataG06Q-MOkYi3kkuU-CNAGtpmU"

def send_discord_message(message: str):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Discord webhook error: {e}")

# Intervals in minutes
intervals = {
    "Amentis": 1740, "General Aqulcus": 1740, "Baron Braudmore": 1920, "Gareth": 1920,
    "Shuliar": 2100, "Larba": 2100, "Catena": 2100, "Lady Dalia": 1080,
    "Titore": 2220, "Duplican": 2880, "Wannitas": 2880, "Metus": 2880,
    "Asta": 3720, "Ordo": 3720, "Secreta": 3720, "Supore": 3720,
}

# Original next times
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

# Compute last times based on next times
last_times_data = []
for name, next_str in zip(boss_names, next_times_str):
    next_time = datetime.strptime(next_str, "%Y-%m-%d %I:%M %p").replace(tzinfo=MANILA)
    interval_sec = intervals[name] * 60
    last_time = next_time - timedelta(seconds=interval_sec)
    last_times_data.append((name, intervals[name], last_time.strftime("%Y-%m-%d %I:%M %p")))

# Other bosses
other_bosses = [
    ("Venatus", 600, "12:31 PM"),("Viorent", 600, "12:32 PM"),("Ego", 1260, "04:32 PM"),
    ("Araneo", 1440, "04:33 PM"),("Livera", 1440, "04:36 PM"),("Undomiel", 1440, "04:42 PM"),
]

timers_data = other_bosses + last_times_data

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

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Lord9 Santiago 7 Boss Timer", layout="wide")
st.title("🛡️ Lord9 Santiago 7 Boss Timer")

# Auto-refresh countdown
st_autorefresh(interval=1000, key="refresh")

# Initialize timers in session_state
if "timers" not in st.session_state:
    st.session_state.timers = [TimerEntry(*data) for data in timers_data]
timers = st.session_state.timers

# ------------------- Build DataFrame -------------------
def build_df(timers_list):
    timers_sorted = sorted(timers_list, key=lambda x: x.countdown())
    df = pd.DataFrame({
        "Name": [t.name for t in timers_sorted],
        "Interval (min)": [t.interval_minutes for t in timers_sorted],
        "Last Time": [t.last_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_sorted],
        "Countdown": [t.format_countdown() for t in timers_sorted],
        "Next Time": [t.next_time.strftime("%Y-%m-%d %I:%M %p") for t in timers_sorted],
        "Status": ["Alive" if t.countdown().total_seconds() > 0 else "Killed" for t in timers_sorted],
        "Color": [t.countdown_color() for t in timers_sorted],
    })
    return df, timers_sorted

df, timers_sorted = build_df(timers)

def color_countdown(s):
    return [f"color: {c}" for c in df["Color"]]

# ------------------- Discord Notifications -------------------
for t in timers:
    if f"{t.name}_5min" not in st.session_state:
        st.session_state[f"{t.name}_5min"] = False
    if f"{t.name}_spawn" not in st.session_state:
        st.session_state[f"{t.name}_spawn"] = False

    remaining = t.countdown().total_seconds()

    # 5-minute warning
    if 0 < remaining <= 300 and not st.session_state[f"{t.name}_5min"]:
        send_discord_message(f"⏰ @everyone {t.name} will spawn in 5 minutes! Next: {t.next_time.strftime('%Y-%m-%d %I:%M %p')}")
        st.session_state[f"{t.name}_5min"] = True

    # Spawn notification
    if remaining <= 0 and not st.session_state[f"{t.name}_spawn"]:
        send_discord_message(f"⚔️ @everyone {t.name} has spawned! Next: {t.next_time.strftime('%Y-%m-%d %I:%M %p')}")
        st.session_state[f"{t.name}_spawn"] = True

# ------------------- Reset All Timers -------------------
if st.button("Reset All Timers"):
    now = datetime.now(tz=MANILA)
    for timer in timers:
        timer.last_time = now
        timer.next_time = now + timedelta(seconds=timer.interval)
        st.session_state[f"{timer.name}_5min"] = False
        st.session_state[f"{timer.name}_spawn"] = False
    df, timers_sorted = build_df(timers)
    send_discord_message(f"♻️ @everyone All boss timers have been reset manually at {now.strftime('%Y-%m-%d %I:%M %p')}.")
    st.success("All timers have been reset to 0 and countdowns start from now!")

# ------------------- Display Table -------------------
st.dataframe(df.drop(columns=["Color"]).style.apply(color_countdown, subset=["Countdown"], axis=0))

# ------------------- Grid-style Edit Panel -------------------
if st.button("Edit Times"):
    with st.expander("Edit Last Time or Next Time (Grid View)", expanded=True):
        num_cols = 3
        for i in range(0, len(timers_sorted), num_cols):
            cols = st.columns(num_cols)
            for j, timer in enumerate(timers_sorted[i:i+num_cols]):
                with cols[j]:
                    st.subheader(timer.name)
                    st.caption("Select Last Time (Date + Time) in Manila GMT+8")
                    last_date = st.date_input("Last Date", value=timer.last_time.date(), key=f"{timer.name}_last_date")
                    last_time = st.time_input("Last Time", value=timer.last_time.time(), key=f"{timer.name}_last_time")
                    new_last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)

                    st.caption("Select Next Time (Date + Time) in Manila GMT+8")
                    next_date = st.date_input("Next Date", value=timer.next_time.date(), key=f"{timer.name}_next_date")
                    next_time = st.time_input("Next Time", value=timer.next_time.time(), key=f"{timer.name}_next_time")
                    new_next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)

                    if new_last_time != timer.last_time or new_next_time != timer.next_time:
                        timer.last_time = new_last_time
                        timer.next_time = new_next_time
                        st.session_state[f"{timer.name}_5min"] = False
                        st.session_state[f"{timer.name}_spawn"] = False
                        send_discord_message(
                            f"⏰ @everyone Timer Updated: {timer.name}\nLast: {timer.last_time.strftime('%Y-%m-%d %I:%M %p')}\nNext: {timer.next_time.strftime('%Y-%m-%d %I:%M %p')}"
                        )

# Refresh DataFrame after edits
df, timers_sorted = build_df(timers)
st.dataframe(df.drop(columns=["Color"]).style.apply(color_countdown, subset=["Countdown"], axis=0))
