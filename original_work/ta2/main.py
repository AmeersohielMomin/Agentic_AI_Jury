#!/usr/bin/env python3
"""Main Entry Point for the Study Schedule Multi-Agent System (TA2).

Runs with one command from README as required by the TA2 SOP:
  python ta2/main.py [options]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from agents.graph import build_study_optimizer_graph
from tools.rag_tool import StudyGuidelinesRAG
from database.profile_store import get_student_profile

SCENARIO_PRESETS = {
    "ready": {
        "user_id": "student_alice",
        "topics_covered": 18,
        "total_topics": 20,
        "days_left": 5,
        "hours_per_topic": 2.0,
        "subject_name": "AI & Agentic Systems",
        "human_decision": "APPROVED",
    },
    "borderline": {
        "user_id": "student_bob",
        "topics_covered": 14,
        "total_topics": 20,
        "days_left": 3,
        "hours_per_topic": 2.0,
        "subject_name": "Operating Systems",
        "human_decision": "APPROVED",
    },
    "crunch": {
        "user_id": "student_charlie",
        "topics_covered": 5,
        "total_topics": 15,
        "days_left": 2,
        "hours_per_topic": 1.5,
        "subject_name": "Algorithms Exam",
        "human_decision": "REJECTED",  # Demonstrating rejected oversight path
    },
}


def run_pipeline(
    user_id: str = "student_alice",
    topics_covered: int = 14,
    total_topics: int = 20,
    days_left: int = 3,
    hours_per_topic: float = 2.0,
    subject_name: str = "AI Exam",
    human_decision: str = "APPROVED",
    rag_instance: StudyGuidelinesRAG | None = None,
) -> Dict[str, Any]:
    """Execute the full multi-agent pipeline."""
    graph = build_study_optimizer_graph(rag_instance=rag_instance)
    profile = get_student_profile(user_id)

    initial_state = {
        "messages": [],
        "user_id": user_id,
        "student_profile": profile,
        "topics_covered": topics_covered,
        "total_topics": total_topics,
        "days_left": days_left,
        "hours_per_topic": hours_per_topic,
        "subject_name": subject_name,
        "readiness_result": None,
        "rag_context": None,
        "workload_result": None,
        "diagnostician_proposal": None,
        "negotiator_counter_bid": None,
        "negotiation_status": "PROPOSED",
        "hop_count": 0,
        "max_hops": 5,
        "requires_human_approval": False,
        "human_decision": human_decision,
        "human_feedback": None,
        "next_node": "guard",
        "final_schedule_plan": None,
        "error_log": [],
    }

    final_state = graph.invoke(initial_state)
    return final_state


def print_trace(state: Dict[str, Any]) -> None:
    print("\n" + "=" * 65)
    print("🤖 TA2 MULTI-AGENT ORCHESTRATION TRACE")
    print("=" * 65)
    print(f"Student: {state.get('user_id')} | Subject: {state.get('subject_name')}")
    print(f"Inputs: Covered={state.get('topics_covered')}/{state.get('total_topics')} | "
          f"Days Left={state.get('days_left')} | Hrs/Topic={state.get('hours_per_topic')}")
    print(f"Total Graph Hops: {state.get('hop_count')}/5")
    print("-" * 65)
    print("MESSAGES & NEGOTIATION LOG:")
    for idx, msg in enumerate(state.get("messages", []), 1):
        sender = msg.get("sender", "unknown").upper()
        content = msg.get("content", "")
        print(f"\n[{idx}] {sender}:")
        print(f"    {content}")
    print("\n" + "-" * 65)
    print(state.get("final_schedule_plan", ""))


def main() -> None:
    parser = argparse.ArgumentParser(description="TA2 Multi-Agent Study Schedule Optimizer")
    parser.add_argument("--scenario", choices=["ready", "borderline", "crunch"], help="Run preset scenario")
    parser.add_argument("--user-id", default="student_alice", help="Student user ID from SQLite")
    parser.add_argument("--covered", type=int, default=14, help="Topics covered")
    parser.add_argument("--total", type=int, default=20, help="Total curriculum topics")
    parser.add_argument("--days", type=int, default=3, help="Days left until exam")
    parser.add_argument("--hours-per-topic", type=float, default=2.0, help="Hours needed per topic")
    parser.add_argument("--subject", default="AI & Agentic Systems", help="Subject name")
    parser.add_argument("--decision", choices=["APPROVED", "REJECTED"], default="APPROVED", help="Human oversight decision")
    parser.add_argument("--save-trace", help="Optional path to save trace text")
    args = parser.parse_args()

    if args.scenario:
        params = SCENARIO_PRESETS[args.scenario]
        user_id = params["user_id"]
        covered = params["topics_covered"]
        total = params["total_topics"]
        days = params["days_left"]
        hours = params["hours_per_topic"]
        subject = params["subject_name"]
        decision = params["human_decision"]
    else:
        user_id = args.user_id
        covered = args.covered
        total = args.total
        days = args.days
        hours = args.hours_per_topic
        subject = args.subject
        decision = args.decision

    state = run_pipeline(
        user_id=user_id,
        topics_covered=covered,
        total_topics=total,
        days_left=days,
        hours_per_topic=hours,
        subject_name=subject,
        human_decision=decision,
    )

    print_trace(state)

    if args.save_trace:
        Path(args.save_trace).parent.mkdir(parents=True, exist_ok=True)
        with open(args.save_trace, "w", encoding="utf-8") as f:
            f.write(state.get("final_schedule_plan", "") + "\n\n")
            f.write(json.dumps(state.get("messages", []), indent=2))
        print(f"\nTrace saved to: {args.save_trace}")


if __name__ == "__main__":
    main()
