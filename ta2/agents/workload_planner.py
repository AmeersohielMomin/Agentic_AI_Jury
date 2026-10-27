"""Workload Planner & Negotiator Specialist Agent (Unit 4).

Role 2 of 5-field spec:
- Name: workload_planner
- Goal: Calculate required study hours per day, verify student profile limits from SQLite, and negotiate realistic daily load.
- Tools: hours_needed_per_day, SQLiteProfileStore
- Inputs / Outputs: (remaining_topics, days_left, student_profile) -> (workload_result, counter_bid, negotiation_status)
- Limits: Cannot modify curriculum requirements; limited to time budgeting and fatigue bounds.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.state import AgentState
from tools.exam_tools import hours_needed_per_day


class WorkloadPlannerNegotiator:
    def process(self, state: AgentState) -> Dict[str, Any]:
        covered = state.get("topics_covered", 0)
        total = state.get("total_topics", 20)
        remaining = max(0, total - covered)
        days = state.get("days_left", 3)
        hours_per_topic = state.get("hours_per_topic", 2.0)
        profile = state.get("student_profile", {})
        
        max_daily_stamina = profile.get("daily_max_hours", 5.0)
        fatigue_cap = profile.get("fatigue_threshold", 4.5)

        # Step 1: Calculate raw required hours
        workload = hours_needed_per_day(remaining, days, hours_per_topic)

        requires_hitl = False
        negotiation_status = "AGREED"
        counter_bid = None

        if workload.status == "SUCCESS":
            calc_hours = workload.raw_value or 0.0

            # Step 2: Negotiation / Bidding logic
            if calc_hours <= fatigue_cap:
                counter_bid = (
                    f"[Negotiator Acceptance]: Planned load of {calc_hours:.2f} hrs/day is well within "
                    f"student stamina limit ({max_daily_stamina:.1f} hrs/day). Schedule accepted without adjustment."
                )
                negotiation_status = "AGREED"
            elif calc_hours <= max_daily_stamina:
                # Moderate crunch zone
                counter_bid = (
                    f"[Negotiator Counter-Bid]: Calculated {calc_hours:.2f} hrs/day approaches maximum stamina "
                    f"({max_daily_stamina:.1f} hrs/day). Counter-bid: Add 15-min decompression breaks between 50-min study blocks."
                )
                negotiation_status = "COUNTERED"
                requires_hitl = True  # High intensity triggers human check
            else:
                # Over-limit burnout zone: Negotiator demands workload compression
                excess = calc_hours - max_daily_stamina
                adjusted_topics = int(max_daily_stamina * days / hours_per_topic)
                counter_bid = (
                    f"[Negotiator Rejection & Counter-Offer]: Demanded {calc_hours:.2f} hrs/day exceeds safe stamina "
                    f"({max_daily_stamina:.1f} hrs/day) by {excess:.2f} hrs/day. "
                    f"Counter-Proposal: Cap daily study at {max_daily_stamina:.1f} hrs/day, covering high-yield {adjusted_topics} topics, "
                    f"and reserve final day for light summary notes to prevent mental exhaustion."
                )
                negotiation_status = "COUNTERED"
                requires_hitl = True
        else:
            counter_bid = f"[Negotiator Failure Handling]: {workload.output}"
            negotiation_status = "FAILED"

        messages = list(state.get("messages", []))
        messages.append({
            "sender": "workload_planner",
            "content": counter_bid,
            "tool_output": workload.output,
        })

        return {
            "workload_result": {
                "status": workload.status,
                "output": workload.output,
                "hours_per_day": workload.raw_value,
            },
            "negotiator_counter_bid": counter_bid,
            "negotiation_status": negotiation_status,
            "requires_human_approval": requires_hitl,
            "messages": messages,
            "hop_count": state.get("hop_count", 0) + 1,
        }
