import os
import random
import uuid
import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# --- CONFIGURATION ---
NUM_USERS = 500
NUM_SESSIONS = 2500
OUTPUT_FILE = "netflix_user_events.csv"

# Categorical options & weights
PLATFORMS = ["Mobile App", "Web", "Tablet", "Smart TV"]
PLATFORM_WEIGHTS = [0.35, 0.25, 0.15, 0.25]

SURFACES = ["Home Screen", "Search Bar", "Category Hub", "Video Player"]
SURFACE_WEIGHTS = [0.45, 0.25, 0.15, 0.15]

EVENT_TYPES = [
    "browse",
    "search_query",
    "select_title",
    "play_start",
    "buffering_stall",
    "ui_error",
    "playback_error",
    "pause",
    "exit_session",
]

# Generate stable list of User IDs
USER_IDS = [f"USR_{1000 + i}" for i in range(NUM_USERS)]


def generate_synthetic_events(num_sessions=2500):
    events = []
    base_timestamp = pd.Timestamp("2026-09-01 00:00:00")

    for _ in range(num_sessions):
        session_id = f"SES_{uuid.uuid4().hex[:10].upper()}"
        user_id = random.choice(USER_IDS)
        platform = np.random.choice(PLATFORMS, p=PLATFORM_WEIGHTS)

        # Randomize start time across a 30-day period
        current_time = base_timestamp + pd.Timedelta(
            seconds=int(np.random.uniform(0, 30 * 24 * 3600))
        )

        # Session behavioral archetype weights
        # 1: Quick watch, 2: Heavy search/browse, 3: High friction (buffering/errors)
        archetype = np.random.choice([1, 2, 3], p=[0.50, 0.35, 0.15])

        # Always start with browsing on Home Screen
        surface = "Home Screen"
        events.append(
            {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": current_time,
                "event_type": "browse",
                "surface": surface,
                "platform": platform,
                "duration_seconds": int(np.random.exponential(scale=15) + 2),
            }
        )

        # Simulate event flows based on archetype
        if archetype == 1:
            # Quick Watch: Search/browse -> Play -> Watch
            current_time += pd.Timedelta(seconds=events[-1]["duration_seconds"])

            # 40% chance of searching first
            if random.random() < 0.4:
                surface = "Search Bar"
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": "search_query",
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": int(
                            np.random.exponential(scale=20) + 5
                        ),
                    }
                )
                current_time += pd.Timedelta(
                    seconds=events[-1]["duration_seconds"]
                )

            # Select and Play
            events.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": current_time,
                    "event_type": "select_title",
                    "surface": surface,
                    "platform": platform,
                    "duration_seconds": random.randint(1, 5),
                }
            )
            current_time += pd.Timedelta(seconds=events[-1]["duration_seconds"])

            surface = "Video Player"
            events.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": current_time,
                    "event_type": "play_start",
                    "surface": surface,
                    "platform": platform,
                    "duration_seconds": 0,
                }
            )

            # Watch duration (Includes both early abandonment < 120s and normal watch)
            watch_duration = (
                int(np.random.exponential(scale=45))
                if random.random() < 0.2
                else int(np.random.uniform(600, 5400))
            )
            current_time += pd.Timedelta(seconds=watch_duration)

            events.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": current_time,
                    "event_type": "exit_session",
                    "surface": surface,
                    "platform": platform,
                    "duration_seconds": watch_duration,
                }
            )

        elif archetype == 2:
            # Search Loop / Abandonment: Multiple searches, no play or delayed play
            surface = "Search Bar"
            search_loops = random.randint(3, 7)

            for _ in range(search_loops):
                dur = int(np.random.exponential(scale=40) + 10)
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": "search_query",
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": dur,
                    }
                )
                current_time += pd.Timedelta(seconds=dur)

            # 60% abandon after searching loop (> 3 mins search), 40% eventually play
            if random.random() < 0.6:
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": "exit_session",
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": 0,
                    }
                )
            else:
                surface = "Video Player"
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": "play_start",
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": 0,
                    }
                )
                watch_dur = int(np.random.uniform(300, 3600))
                current_time += pd.Timedelta(seconds=watch_dur)
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": "exit_session",
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": watch_dur,
                    }
                )

        else:
            # Technical Issues: Stalls, UI errors, Playback errors
            surface = "Video Player"
            events.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": current_time,
                    "event_type": "play_start",
                    "surface": surface,
                    "platform": platform,
                    "duration_seconds": 0,
                }
            )

            # Add buffering stalls / errors
            for _ in range(random.randint(1, 3)):
                stall_dur = random.randint(2, 25)
                current_time += pd.Timedelta(seconds=stall_dur)
                events.append(
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "timestamp": current_time,
                        "event_type": random.choice(
                            ["buffering_stall", "ui_error", "playback_error"]
                        ),
                        "surface": surface,
                        "platform": platform,
                        "duration_seconds": stall_dur,
                    }
                )

            events.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": current_time,
                    "event_type": "exit_session",
                    "surface": surface,
                    "platform": platform,
                    "duration_seconds": 0,
                }
            )

    df = pd.DataFrame(events)
    df = df.sort_values(by=["session_id", "timestamp"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    print("Generating synthetic event dataset...")
    df_events = generate_synthetic_events(NUM_SESSIONS)
    df_events.to_csv(OUTPUT_FILE, index=False)

    print(f"Dataset successfully created: '{OUTPUT_FILE}'")
    print(f"Total Events Generated: {len(df_events)}")
    print("\nData Sample:")
    print(df_events.head(10))


