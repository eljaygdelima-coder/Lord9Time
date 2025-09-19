import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from streamlit_autorefresh import st_autorefresh

# Manila timezone
MANILA = ZoneInfo("Asia/Manila")

# Discord webhook URL
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_HERE"

# Autorefresh every 60 sec
st_autorefresh(interval=60 * 1000, key="boss_timer_refresh")

# Session state
if "discord_flags" not in st.session_state:
    st.session_state.discord_flags = {}
if "timers" not in st.session_state:
    st.session_state.timers = []
if "unique_timers" not in st.session_state:
    st.session_state.unique_timers = []

# Timer class
class TimerEntry:
    def __init__(self, name, interval, last_time):
        self.name = name
        self.interval = interval  # in minutes
        self.last_time = last_time
        self.next_time = last_time + timedelta(minutes=interval)

    def countdown(self):
        remaining = self.next_time - datetime.now(MANILA)
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

# Discord notification
def send_discord_notification(message):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        st.error(f"Discord error: {e}")

# Update Discord notifications
def check_and_notify(timer):
    now = datetime.now(MANILA)
    flag_5 = f"{timer.name}_5min"
    flag_spawn = f"{timer.name}_spawn"

    # Initialize flags if missing
    if flag_5 not in st.session_state.discord_flags:
        st.session_state.discord_flags[flag_5] = False
    if flag_spawn not in st.session_state.discord_flags:
        st.session_state.discord_flags[flag_spawn] = False

    # 5 minutes before spawn
    if 0 < (timer.next_time - now).total_seconds() <= 300:
        if not st.session_state.discord_flags[flag_5]:
            send_discord_notification(
                f"⏰ @everyone {timer.name} will spawn in 5 minutes! Next: {timer.next_time.strftime('%Y-%m-%d %I:%M %p')}"
            )
            st.session_state.discord_flags[flag_5] = True

    # At spawn
    if abs((timer.next_time - now).total_seconds()) <= 30:
        if not st.session_state.discord_flags[flag_spawn]:
            send_discord_notification(
                f"⚔️ @everyone {timer.name} has spawned! ({timer.next_time.strftime('%Y-%m-%d %I:%M %p')})"
            )
            st.session_state.discord_flags[flag_spawn] = True

    # Reset after spawn
    if now > timer.next_time + timedelta(minutes=1):
        st.session_state.discord_flags[flag_5] = False
        st.session_state.discord_flags[flag_spawn] = False

# Display table
def render_table(timers):
    if not timers:
        st.info("No bosses added yet.")
        return

    data = []
    for t in timers:
        data.append([
            t.name,
            t.interval,
            t.last_time.strftime("%Y-%m-%d %I:%M %p"),
            str(t.countdown()).split(".")[0],
            t.next_time.strftime("%Y-%m-%d %I:%M %p")
        ])
    df = pd.DataFrame(data, columns=["Boss Name", "Interval (min)", "Time Killed", "Countdown", "Next Spawn"])
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Tabs ---
tabs = st.tabs(["World Boss Spawn", "Manage & Edit Timers", "Unique Bosses Spawn", "Manage & Edit Unique Bosses"])

# TAB 1: World Boss Spawn
with tabs[0]:
    st.subheader("🌍 World Boss Spawn Table")
    for timer in st.session_state.timers:
        check_and_notify(timer)
    render_table(st.session_state.timers)

# TAB 2: Manage & Edit Timers
with tabs[1]:
    st.subheader("⚙️ Manage & Edit World Boss Timers")

    for timer in st.session_state.timers:
        st.markdown(f"### {timer.name}")
        with st.form(f"edit_{timer.name}"):
            col1, col2 = st.columns(2)
            with col1:
                last_date = st.date_input("Last Date", value=timer.last_time.date(), key=f"{timer.name}_ld")
                last_time = st.time_input("Last Time", value=timer.last_time.time(), key=f"{timer.name}_lt")
            with col2:
                next_date = st.date_input("Next Date", value=timer.next_time.date(), key=f"{timer.name}_nd")
                next_time = st.time_input("Next Time", value=timer.next_time.time(), key=f"{timer.name}_nt")

            save_changes = st.form_submit_button("💾 Save Changes")
            if save_changes:
                timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
                st.session_state.discord_flags[f"{timer.name}_5min"] = False
                st.session_state.discord_flags[f"{timer.name}_spawn"] = False
                st.success(f"{timer.name} updated successfully!")

# TAB 3: Unique Bosses Spawn
with tabs[2]:
    st.subheader("🧩 Unique Bosses Spawn Table")
    render_table(st.session_state.unique_timers)

# TAB 4: Manage & Edit Unique Bosses
with tabs[3]:
    st.subheader("⚙️ Manage & Edit Unique Bosses")

    for timer in st.session_state.unique_timers:
        st.markdown(f"### {timer.name}")
        with st.form(f"edit_unique_{timer.name}"):
            col1, col2 = st.columns(2)
            with col1:
                last_date = st.date_input("Last Date", value=timer.last_time.date(), key=f"{timer.name}_uld")
                last_time = st.time_input("Last Time", value=timer.last_time.time(), key=f"{timer.name}_ult")
            with col2:
                next_date = st.date_input("Next Date", value=timer.next_time.date(), key=f"{timer.name}_und")
                next_time = st.time_input("Next Time", value=timer.next_time.time(), key=f"{timer.name}_unt")

            save_changes = st.form_submit_button("💾 Save Changes")
            if save_changes:
                timer.last_time = datetime.combine(last_date, last_time).replace(tzinfo=MANILA)
                timer.next_time = datetime.combine(next_date, next_time).replace(tzinfo=MANILA)
                st.success(f"{timer.name} updated successfully!")
