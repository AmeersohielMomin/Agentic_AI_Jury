"""Seed script to populate initial student profiles in SQLite.

Fulfills TA2 submission requirement: 'Include a seed script for the SQLite store'.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.profile_store import DEFAULT_DB_PATH, SQLiteProfileStore


def seed_database(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    store = SQLiteProfileStore(db_path)

    # Student 1: Alice (Steady learner, max 5 hours/day)
    alice_profile = {
        "name": "Alice Smith",
        "daily_max_hours": 5.0,
        "pace_multiplier": 1.0,
        "fatigue_threshold": 4.5,
        "target_subject": "AI & Agentic Systems",
        "study_preference": "morning_blocks",
        "notes": "Prefers consistent daily load; experiences burnout above 5 hours.",
    }
    for k, v in alice_profile.items():
        store.put("student_alice", "profile", k, v)

    # Student 2: Bob (Crunch learner, high stamina up to 8 hours, slower reading pace)
    bob_profile = {
        "name": "Bob Vance",
        "daily_max_hours": 8.0,
        "pace_multiplier": 1.25,
        "fatigue_threshold": 6.5,
        "target_subject": "Operating Systems & Networking",
        "study_preference": "night_cramming",
        "notes": "Can handle intensive blocks but requires 25% extra reading time.",
    }
    for k, v in bob_profile.items():
        store.put("student_bob", "profile", k, v)

    # Student 3: Charlie (Part-time student, strict max 3.5 hours/day due to work)
    charlie_profile = {
        "name": "Charlie Day",
        "daily_max_hours": 3.5,
        "pace_multiplier": 0.9,
        "fatigue_threshold": 3.0,
        "target_subject": "Data Structures & Algorithms",
        "study_preference": "weekend_intensive",
        "notes": "Working student; daily study cap strictly 3.5h.",
    }
    for k, v in charlie_profile.items():
        store.put("student_charlie", "profile", k, v)

    print(f"[Seed] Successfully seeded SQLite store at: {db_path}")
    print("[Seed] Profiles created for:")
    for uid in ["student_alice", "student_bob", "student_charlie"]:
        data = store.get_all(uid, "profile")
        print(f"  - {uid}: {data.get('name')} (Max hours/day: {data.get('daily_max_hours')})")


if __name__ == "__main__":
    seed_database()
