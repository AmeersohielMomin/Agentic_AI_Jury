"""Long-term persistent profile memory backed by SQLite.

Implements U3-2:
- Namespaced key-value store: (user_id, "profile")
- Survives process restart
- Evidence demo: Write profile -> Process Termination simulation -> Read profile back
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.profile_store import DEFAULT_DB_PATH, SQLiteProfileStore


def run_long_term_restart_demo(db_path: Path = DEFAULT_DB_PATH) -> Dict[str, Any]:
    user_id = "student_eva"
    namespace = "profile"

    # Step 1: Initial session - store student personalized study preferences
    store_session_1 = SQLiteProfileStore(db_path)
    initial_profile = {
        "name": "Eva Rostova",
        "target_subject": "Advanced Agentic AI & RAG",
        "daily_max_hours": 4.5,
        "burnout_threshold": 4.0,
        "pace_multiplier": 1.15,
        "preferred_study_time": "early_morning",
        "notes": "Prefers 45-min Pomodoro cycles with short intervals.",
    }

    for key, value in initial_profile.items():
        store_session_1.put(user_id, namespace, key, value)

    # Step 2: Simulate process termination (delete Python store instance from memory)
    del store_session_1
    time.sleep(0.5)

    # Step 3: Fresh process / restart - instantiate new connection to SQLite file
    store_session_2 = SQLiteProfileStore(db_path)
    recalled_profile = store_session_2.get_all(user_id, namespace=namespace)

    # Step 4: Verify persistence integrity
    is_identical = (recalled_profile == initial_profile)

    return {
        "user_id": user_id,
        "namespace": namespace,
        "stored_data": initial_profile,
        "recalled_data": recalled_profile,
        "restart_successful": is_identical,
    }


if __name__ == "__main__":
    print("=== Long-Term Memory SQLite Restart Demo (U3-2) ===")
    demo = run_long_term_restart_demo()
    print(f"User ID: {demo['user_id']}")
    print(f"Namespace: ({demo['user_id']}, '{demo['namespace']}')")
    print(f"Restart Persistence Verified: {demo['restart_successful']}")
    print("\nRecalled Profile Post-Restart:")
    for k, v in demo["recalled_data"].items():
        print(f"  • {k}: {v}")
