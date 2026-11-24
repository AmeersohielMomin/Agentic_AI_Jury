"""Compiled LangGraph Multi-Agent Workflow with Supervisor, Negotiation, and HITL.

Connects:
- Input Safety Guard
- Supervisor Orchestrator (MAX_HOPS=5)
- Readiness Diagnostician Specialist (TA1 Tool 1 + RAG)
- Workload Planner & Negotiator Specialist (TA1 Tool 2 + SQLite Profile)
- Human Approval Oversight Node
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.state import AgentState
from agents.diagnostician import ReadinessDiagnostician
from agents.workload_planner import WorkloadPlannerNegotiator
from agents.supervisor import SupervisorAgent
from guardrails.input_guard import InputSafetyGuard
from database.profile_store import get_student_profile
from tools.rag_tool import StudyGuidelinesRAG


def build_study_optimizer_graph(
    rag_instance: StudyGuidelinesRAG | None = None,
    max_hops: int = 5,
    checkpointer: Any = None,
):
    diagnostician_agent = ReadinessDiagnostician(rag_instance)
    workload_agent = WorkloadPlannerNegotiator()
    supervisor_agent = SupervisorAgent(max_hops=max_hops)
    guard = InputSafetyGuard()

    # --- Node Definitions ---
    def guard_node(state: AgentState) -> Dict[str, Any]:
        user_input = state.get("subject_name", "") + " " + str(state.get("messages", []))
        guard_res = guard.inspect_and_filter(user_input)
        if not guard_res.is_safe:
            return {
                "final_schedule_plan": f"[SECURITY REJECTION]: {guard_res.rejection_reason}",
                "error_log": state.get("error_log", []) + [guard_res.rejection_reason or ""],
                "next_node": "end",
            }
        
        # Load user profile from SQLite if not present
        uid = state.get("user_id", "student_alice")
        profile = state.get("student_profile") or get_student_profile(uid)
        return {"student_profile": profile, "next_node": "diagnostician"}

    def diagnostician_node(state: AgentState) -> Dict[str, Any]:
        return diagnostician_agent.process(state)

    def workload_node(state: AgentState) -> Dict[str, Any]:
        return workload_agent.process(state)

    def human_approval_node(state: AgentState) -> Dict[str, Any]:
        decision = state.get("human_decision", "APPROVED")
        messages = list(state.get("messages", []))
        messages.append({
            "sender": "human_oversight",
            "content": f"[Human Decision Recorded]: {decision}",
        })
        return {
            "human_decision": decision,
            "messages": messages,
            "hop_count": state.get("hop_count", 0) + 1,
        }

    def synthesis_node(state: AgentState) -> Dict[str, Any]:
        return supervisor_agent.synthesize_plan(state)

    def hop_limit_node(state: AgentState) -> Dict[str, Any]:
        msg = f"[SAFETY LIMIT]: MAX_HOPS limit ({max_hops}) reached. Halting cycle to prevent infinite loop."
        messages = list(state.get("messages", []))
        messages.append({"sender": "supervisor_agent", "content": msg})
        return {
            "final_schedule_plan": msg,
            "error_log": state.get("error_log", []) + [msg],
            "messages": messages,
        }

    # Routing condition from supervisor
    def supervisor_condition(state: AgentState) -> str:
        if state.get("error_log"):
            return "end"
        return supervisor_agent.route_next_step(state)

    # --- Graph Assembly ---
    builder = StateGraph(AgentState)
    builder.add_node("guard", guard_node)
    builder.add_node("diagnostician", diagnostician_node)
    builder.add_node("workload_planner", workload_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("synthesize_final_plan", synthesis_node)
    builder.add_node("hop_limit_reached", hop_limit_node)

    builder.add_edge(START, "guard")

    def route_after_guard(state: AgentState) -> str:
        if state.get("next_node") == "end":
            return END
        return "diagnostician"

    builder.add_conditional_edges("guard", route_after_guard, {"diagnostician": "diagnostician", END: END})
    builder.add_conditional_edges("diagnostician", supervisor_condition, {
        "workload_planner": "workload_planner",
        "human_approval": "human_approval",
        "synthesize_final_plan": "synthesize_final_plan",
        "hop_limit_reached": "hop_limit_reached",
    })
    builder.add_conditional_edges("workload_planner", supervisor_condition, {
        "human_approval": "human_approval",
        "synthesize_final_plan": "synthesize_final_plan",
        "hop_limit_reached": "hop_limit_reached",
    })
    builder.add_edge("human_approval", "synthesize_final_plan")
    builder.add_edge("synthesize_final_plan", END)
    builder.add_edge("hop_limit_reached", END)

    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()
