"""Supervisor Orchestrator Agent (Unit 4).

Role 3 of 5-field spec:
- Name: supervisor_agent
- Goal: Coordinate specialist agents, manage MAX_HOPS budget, trigger human approval when needed, and finalize schedule.
- Tools: State routing, MAX_HOPS counter, oversight router
- Inputs / Outputs: AgentState -> Next Node or Final Schedule Synthesis
- Limits: Strict hop count ceiling (MAX_HOPS=5) to prevent unbounded loops.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Literal

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.state import AgentState
from agents.diagnostician import ReadinessDiagnostician
from agents.workload_planner import WorkloadPlannerNegotiator


class SupervisorAgent:
    def __init__(self, max_hops: int = 5) -> None:
        self.max_hops = max_hops

    def route_next_step(self, state: AgentState) -> str:
        """Evaluate current state and route to next appropriate node."""
        hop = state.get("hop_count", 0)
        if hop >= self.max_hops:
            return "hop_limit_reached"

        # If readiness has not been evaluated, route to Diagnostician
        if not state.get("readiness_result"):
            return "diagnostician"

        # If workload has not been evaluated, route to Workload Planner
        if not state.get("workload_result"):
            return "workload_planner"

        # Check if human oversight is pending
        if state.get("requires_human_approval") and state.get("human_decision") == "PENDING":
            return "human_approval"

        return "synthesize_final_plan"

    def synthesize_plan(self, state: AgentState) -> Dict[str, Any]:
        """Synthesize final multi-agent agreement into actionable study plan."""
        readiness = state.get("readiness_result", {})
        workload = state.get("workload_result", {})
        profile = state.get("student_profile", {})
        human_decision = state.get("human_decision", "APPROVED")
        negotiation_status = state.get("negotiation_status", "AGREED")

        lines = [
            "============================================================",
            "🎓 MULTI-AGENT FINAL STUDY OPTIMIZATION PLAN",
            "============================================================",
            f"Student: {profile.get('name', 'Learner')} (User ID: {state.get('user_id', 'unknown')})",
            f"Subject: {state.get('subject_name', 'Examination')}",
            f"Readiness Assessment: {readiness.get('output', 'N/A')}",
            f"Calculated Daily Workload: {workload.get('output', 'N/A')}",
            f"Institutional Policy Ref: {state.get('rag_context', 'General Curriculum Benchmark')}",
            f"Multi-Agent Negotiation Status: {negotiation_status}",
        ]

        if state.get("requires_human_approval"):
            lines.append(f"Human Oversight Decision: {human_decision}")
            if human_decision == "REJECTED":
                lines.append("Note: Intensive schedule was REJECTED by human oversight. Student advised to request syllabus extension.")
            else:
                lines.append("Note: Intensive schedule was formally APPROVED by human oversight.")

        lines.append("============================================================")
        final_text = "\n".join(lines)

        messages = list(state.get("messages", []))
        messages.append({
            "sender": "supervisor_agent",
            "content": final_text,
        })

        return {
            "final_schedule_plan": final_text,
            "messages": messages,
            "hop_count": state.get("hop_count", 0) + 1,
        }
