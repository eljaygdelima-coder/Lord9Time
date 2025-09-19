import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Manila timezone
TIMEZONE = ZoneInfo("Asia/Manila")

# Boss data (Name, Interval in minutes, Last Time)
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

# Convert to DataFrame
def create_dataframe():
    df = pd.DataFrame(boss_data, columns=["Boss Name", "Interval (min)", "Last Time"])
    df["Last Time"] = pd.to_datetime(df["Last Time"], format="%Y-%m-%d %I:%M %p").dt.tz_localize(TIMEZONE)

    # Compute Next Spawn
    df["Next Spawn"] = df["Last Time"] + pd.to_timedelta(df["Interval (min)"], unit="m")

    # Compute Countdown
    now = datetime.now(TIMEZONE)
    df["Countdown"] = df["Next Spawn"] - now
    df["Countdown"] = df["Countdown"].apply(lambda x: str(x).split(".")[0])  # remove microseconds

    return df

# Streamlit app
st.set_page_config("Boss Timer", layout="wide")
st.title("📅 Boss Timer Tracker")

# Load current data
df = create_dataframe()

# Display editable only for Last Time
st.subheader("Manage Boss Timers (Edit Last Time Only)")
edited_df = st.data_editor(
    df,
    column_config={
        "Boss Name": st.column_config.TextColumn(disabled=True),
        "Interval (min)": st.column_config.NumberColumn(disabled=True),
        "Next Spawn": st.column_config.DatetimeColumn(disabled=True),
        "Countdown": st.column_config.TextColumn(disabled=True),
        "Last Time": st.column_config.DatetimeColumn(
            label="Last Time",
            help="Edit the last kill time here to update the timer",
        ),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
)

# Save changes button
if st.button("💾 Save Changes"):
    st.session_state["boss_data"] = edited_df[["Boss Name", "Interval (min)", "Last Time"]].values.tolist()
    st.success("Boss data updated successfully!")

# Refresh countdown
st.subheader("⏱ Updated Timers")
df = create_dataframe()
st.dataframe(df, use_container_width=True)
