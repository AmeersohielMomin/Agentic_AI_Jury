"""Comprehensive Automated Benchmark & Evidence Generator for TA2.

Executes all 8 components (U3-1 to U4-4) and the EV 5-case evaluation,
saving clean trace files into traces/ directory for submission.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Setup paths
TA2_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TA2_DIR.parent
TRACES_DIR = PROJECT_ROOT / "traces"
TRACES_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TA2_DIR))

# TA1 baseline imports
from ta1.study_schedule_optimizer import (
    check_exam_readiness as ta1_readiness,
    hours_needed_per_day as ta1_hours,
)

# TA2 imports
from tools.exam_tools import (
    check_exam_readiness as ta2_readiness,
    hours_needed_per_day as ta2_hours,
)
from tools.rag_tool import StudyGuidelinesRAG
from memory.short_term import run_short_term_memory_demo
from memory.long_term import run_long_term_restart_demo
from guardrails.input_guard import run_injection_comparison_demo
from main import run_pipeline

# Standard 5 Benchmark Test Cases
TEST_CASES = [
    {
        "id": "TC1",
        "name": "Fully Prepared Student",
        "covered": 20,
        "total": 20,
        "days": 5,
        "hrs_per_topic": 2.0,
        "user_id": "student_alice",
        "human_decision": "APPROVED",
        "expected_status": "Ready (100%)",
    },
    {
        "id": "TC2",
        "name": "Borderline Readiness",
        "covered": 16,
        "total": 20,
        "days": 4,
        "hrs_per_topic": 1.5,
        "user_id": "student_bob",
        "human_decision": "APPROVED",
        "expected_status": "Ready (80%)",
    },
    {
        "id": "TC3",
        "name": "Urgent Catch-up Crunch",
        "covered": 5,
        "total": 12,
        "days": 2,
        "hrs_per_topic": 1.5,
        "user_id": "student_charlie",
        "human_decision": "REJECTED",  # High load triggers refusal
        "expected_status": "Not Ready (41.7%), Over-capacity",
    },
    {
        "id": "TC4",
        "name": "Extreme Workload Overload",
        "covered": 2,
        "total": 20,
        "days": 1,
        "hrs_per_topic": 2.5,
        "user_id": "student_charlie",
        "human_decision": "REJECTED",
        "expected_status": "Exceeds daily human biological cap",
    },
    {
        "id": "TC5",
        "name": "Boundary / Zero Days Left",
        "covered": 10,
        "total": 20,
        "days": 0,  # Boundary test: TA1 raises ValueError, TA2 handles gracefully
        "hrs_per_topic": 2.0,
        "user_id": "student_bob",
        "human_decision": "REJECTED",
        "expected_status": "Input Error Caught & Explained",
    },
]


def run_unit3_evidence() -> None:
    print("\n>>> Generating Unit 3 Evidence Traces...")

    # U3-1: Short-term memory
    u3_1_res = run_short_term_memory_demo()
    u3_1_path = TRACES_DIR / "u3_1_short_term_memory.txt"
    with open(u3_1_path, "w", encoding="utf-8") as f:
        f.write("=== U3-1: Short-term Memory (Checkpointer & thread_id) ===\n\n")
        f.write("--- WITH MEMORY (Context Retained) ---\n")
        f.write(f"Turn 1 User: {u3_1_res['with_memory']['turn1_user']}\n")
        f.write(f"Turn 1 AI:   {u3_1_res['with_memory']['turn1_ai']}\n\n")
        f.write(f"Turn 2 User: {u3_1_res['with_memory']['turn2_user']}\n")
        f.write(f"Turn 2 AI:   {u3_1_res['with_memory']['turn2_ai']}\n\n")
        f.write("--- WITHOUT MEMORY (Amnesia Demonstrated) ---\n")
        f.write(f"Turn 1 User: {u3_1_res['without_memory']['turn1_user']}\n")
        f.write(f"Turn 1 AI:   {u3_1_res['without_memory']['turn1_ai']}\n\n")
        f.write(f"Turn 2 User: {u3_1_res['without_memory']['turn2_user']}\n")
        f.write(f"Turn 2 AI:   {u3_1_res['without_memory']['turn2_ai']}\n")
    print(f"  [OK] Saved: {u3_1_path}")

    # U3-2: Long-term memory restart demo
    u3_2_res = run_long_term_restart_demo()
    u3_2_path = TRACES_DIR / "u3_2_long_term_memory.txt"
    with open(u3_2_path, "w", encoding="utf-8") as f:
        f.write("=== U3-2: Long-term Memory (SQLite Namespace & Process Restart) ===\n\n")
        f.write(f"User ID: {u3_2_res['user_id']}\n")
        f.write(f"Namespace: ({u3_2_res['user_id']}, '{u3_2_res['namespace']}')\n")
        f.write(f"Restart Persistence Verified: {u3_2_res['restart_successful']}\n\n")
        f.write("Initial Stored Profile (Session 1):\n")
        f.write(json.dumps(u3_2_res['stored_data'], indent=2) + "\n\n")
        f.write("Recalled Profile After Process Restart (Session 2):\n")
        f.write(json.dumps(u3_2_res['recalled_data'], indent=2) + "\n")
    print(f"  [OK] Saved: {u3_2_path}")

    # U3-3: Chroma RAG k=1 vs k=3 + unanswerable query
    rag = StudyGuidelinesRAG()
    test_q = "What is the maximum allowed daily study hours before burnout oversight is required?"
    res_k1 = rag.answer_query(test_q, k=1)
    res_k3 = rag.answer_query(test_q, k=3)
    res_unans = rag.answer_query("What is the cafeteria lunch menu or parking rate for exam week?", k=3)

    u3_3_path = TRACES_DIR / "u3_3_rag_k1_vs_k3.txt"
    with open(u3_3_path, "w", encoding="utf-8") as f:
        f.write("=== U3-3: Chroma RAG (nomic-embed-text & Grounded Prompt) ===\n\n")
        f.write(f"Query: {test_q}\n\n")
        f.write("--- k=1 Retrieval ---\n")
        f.write(f"Chunks Retrieved: {len(res_k1['retrieved_chunks'])}\n")
        f.write(f"Chunk 1: {res_k1['retrieved_chunks'][0]['title']}\n")
        f.write(f"Answer (k=1): {res_k1['answer']}\n\n")
        f.write("--- k=3 Retrieval ---\n")
        f.write(f"Chunks Retrieved: {len(res_k3['retrieved_chunks'])}\n")
        for idx, c in enumerate(res_k3['retrieved_chunks'], 1):
            f.write(f"  Chunk {idx}: {c['title']}\n")
        f.write(f"Answer (k=3): {res_k3['answer']}\n\n")
        f.write("--- Grounded Refusal on Unanswerable Query ---\n")
        f.write(f"Query: {res_unans['query']}\n")
        f.write(f"Answer: {res_unans['answer']}\n")
    print(f"  [OK] Saved: {u3_3_path}")

    # U3-4: Tool Failure Handling
    u3_4_path = TRACES_DIR / "u3_4_tool_failure.txt"
    fail_res1 = ta2_hours(remaining_topics=6, days_left=0, hours_per_topic=2.0)
    fail_res2 = ta2_readiness(topics_covered=25, total_topics=20)
    with open(u3_4_path, "w", encoding="utf-8") as f:
        f.write("=== U3-4: Tool & Failure Handling (Defensive Recovery Trace) ===\n\n")
        f.write("Test 1: Zero days left input to hours_needed_per_day\n")
        f.write(f"  Status: {fail_res1.status}\n")
        f.write(f"  Error Type: {fail_res1.error_type}\n")
        f.write(f"  Message: {fail_res1.output}\n")
        f.write(f"  Suggested Recovery: {fail_res1.suggested_action}\n\n")
        f.write("Test 2: Overflow topics covered (25/20) input to check_exam_readiness\n")
        f.write(f"  Status: {fail_res2.status}\n")
        f.write(f"  Error Type: {fail_res2.error_type}\n")
        f.write(f"  Message: {fail_res2.output}\n")
        f.write(f"  Suggested Recovery: {fail_res2.suggested_action}\n")
    print(f"  [OK] Saved: {u3_4_path}")


def run_unit4_evidence() -> None:
    print("\n>>> Generating Unit 4 Evidence Traces...")

    # U4-2: Multi-agent routing & negotiation
    state_neg = run_pipeline(
        user_id="student_charlie",
        topics_covered=6,
        total_topics=15,
        days_left=2,
        hours_per_topic=1.5,
        subject_name="Algorithms Exam",
        human_decision="APPROVED",
    )
    u4_2_path = TRACES_DIR / "u4_2_multiagent_routing.txt"
    with open(u4_2_path, "w", encoding="utf-8") as f:
        f.write("=== U4-2: Multi-Agent Supervisor Routing & Negotiation Trace ===\n\n")
        f.write(f"Hop Count: {state_neg.get('hop_count')}/5 (Enforced MAX_HOPS=5)\n")
        f.write(f"Negotiation Status: {state_neg.get('negotiation_status')}\n\n")
        for idx, m in enumerate(state_neg.get("messages", []), 1):
            f.write(f"[{idx}] {m.get('sender', '').upper()}:\n{m.get('content')}\n\n")
        f.write("Final Plan:\n" + state_neg.get("final_schedule_plan", "") + "\n")
    print(f"  [OK] Saved: {u4_2_path}")

    # U4-3: Oversight (Approved vs Rejected paths)
    state_appr = run_pipeline(
        user_id="student_alice",
        topics_covered=10,
        total_topics=20,
        days_left=2,
        hours_per_topic=2.0,
        human_decision="APPROVED",
    )
    state_rej = run_pipeline(
        user_id="student_alice",
        topics_covered=10,
        total_topics=20,
        days_left=2,
        hours_per_topic=2.0,
        human_decision="REJECTED",
    )
    u4_3_hitl_path = TRACES_DIR / "u4_3_oversight_hitl.txt"
    with open(u4_3_hitl_path, "w", encoding="utf-8") as f:
        f.write("=== U4-3: Human Oversight Dual Path (Approved vs Rejected) ===\n\n")
        f.write("--- PATH A: HUMAN APPROVED ---\n")
        f.write(state_appr.get("final_schedule_plan", "") + "\n\n")
        f.write("--- PATH B: HUMAN REJECTED ---\n")
        f.write(state_rej.get("final_schedule_plan", "") + "\n")
    print(f"  [OK] Saved: {u4_3_hitl_path}")

    # U4-3: Guardrail Injection Demo
    u4_3_guard_path = TRACES_DIR / "u4_3_guardrail_injection.txt"
    inj_demo = run_injection_comparison_demo()
    with open(u4_3_guard_path, "w", encoding="utf-8") as f:
        f.write("=== U4-3: Guardrail Defense Against Prompt Injection ===\n\n")
        f.write(f"Attacker Prompt: {inj_demo['attack_prompt']}\n\n")
        f.write(f"BEFORE Guardrail: {inj_demo['without_guardrail']}\n\n")
        f.write(f"AFTER Guardrail:  {inj_demo['with_guardrail']}\n")
    print(f"  [OK] Saved: {u4_3_guard_path}")


def run_5_test_cases_evaluation() -> None:
    print("\n>>> Running 5 Benchmark Cases (EV & U4-4 Challenge Analysis)...")
    ta1_results = []
    ta2_results = []
    metrics = []

    rag = StudyGuidelinesRAG()

    for tc in TEST_CASES:
        cid = tc["id"]
        cname = tc["name"]
        cov = tc["covered"]
        tot = tc["total"]
        rem = tot - cov
        days = tc["days"]
        hpt = tc["hrs_per_topic"]
        uid = tc["user_id"]
        decision = tc["human_decision"]

        # --- RUN TA1 ---
        t0 = time.perf_counter()
        ta1_err = None
        ta1_ready_str = ""
        ta1_hours_str = ""
        try:
            ta1_ready_str = ta1_readiness(cov, tot)
        except Exception as e:
            ta1_err = f"Readiness Error: {e}"

        try:
            if days > 0:
                ta1_hours_str = ta1_hours(rem, days, hpt)
            else:
                ta1_hours(rem, days, hpt)  # Will raise ValueError
        except Exception as e:
            ta1_err = f"Hours Error: {e}" if not ta1_err else f"{ta1_err}; {e}"
        t1 = time.perf_counter()
        ta1_lat_ms = (t1 - t0) * 1000

        ta1_output = ta1_err if ta1_err else f"{ta1_ready_str} | {ta1_hours_str}"
        ta1_results.append({
            "id": cid,
            "name": cname,
            "output": ta1_output,
            "latency_ms": ta1_lat_ms,
            "crashed": ta1_err is not None,
        })

        # --- RUN TA2 ---
        t2 = time.perf_counter()
        ta2_state = run_pipeline(
            user_id=uid,
            topics_covered=cov,
            total_topics=tot,
            days_left=days,
            hours_per_topic=hpt,
            subject_name="Academic Exam",
            human_decision=decision,
            rag_instance=rag,
        )
        t3 = time.perf_counter()
        ta2_lat_ms = (t3 - t2) * 1000

        ta2_output = ta2_state.get("final_schedule_plan", "")
        ta2_results.append({
            "id": cid,
            "name": cname,
            "output": ta2_output,
            "hops": ta2_state.get("hop_count", 0),
            "negotiation": ta2_state.get("negotiation_status"),
            "latency_ms": ta2_lat_ms,
            "crashed": False,  # Never crashes due to defensive failure routing
        })

        metrics.append({
            "id": cid,
            "name": cname,
            "ta1_lat_ms": round(ta1_lat_ms, 2),
            "ta2_lat_ms": round(ta2_lat_ms, 2),
            "ta1_status": "Unhandled Exception (Crash)" if ta1_err else "Deterministic Single-pass",
            "ta2_status": f"Negotiated ({ta2_state.get('negotiation_status')}, {ta2_state.get('hop_count')} hops)",
        })

    # Save TA1 trace
    ev_ta1_path = TRACES_DIR / "ev_ta1_baseline_5cases.txt"
    with open(ev_ta1_path, "w", encoding="utf-8") as f:
        f.write("=== EV: 5 Benchmark Test Cases on TA1 Baseline ===\n\n")
        for r in ta1_results:
            f.write(f"[{r['id']}] {r['name']}\n")
            f.write(f"Latency: {r['latency_ms']:.2f} ms | Crashed: {r['crashed']}\n")
            f.write(f"Result: {r['output']}\n\n")
    print(f"  [OK] Saved: {ev_ta1_path}")

    # Save TA2 trace
    ev_ta2_path = TRACES_DIR / "ev_ta2_extended_5cases.txt"
    with open(ev_ta2_path, "w", encoding="utf-8") as f:
        f.write("=== EV: 5 Benchmark Test Cases on TA2 Extended Multi-Agent System ===\n\n")
        for r in ta2_results:
            f.write(f"[{r['id']}] {r['name']}\n")
            f.write(f"Latency: {r['latency_ms']:.2f} ms | Hops: {r['hops']} | Negotiation: {r['negotiation']}\n")
            f.write(f"Final Schedule:\n{r['output']}\n\n")
    print(f"  [OK] Saved: {ev_ta2_path}")

    # Save U4-4 Challenge Metrics Table
    u4_4_path = TRACES_DIR / "u4_4_challenge_metrics.txt"
    with open(u4_4_path, "w", encoding="utf-8") as f:
        f.write("=== U4-4: Challenge Analysis (Latency, Error Propagation, Hop Budget) ===\n\n")
        f.write("| Case | Scenario Description | TA1 Latency (ms) | TA2 Latency (ms) | TA1 Robustness | TA2 Coordination |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for m in metrics:
            f.write(f"| {m['id']} | {m['name']} | {m['ta1_lat_ms']} | {m['ta2_lat_ms']} | {m['ta1_status']} | {m['ta2_status']} |\n")
    print(f"  [OK] Saved: {u4_4_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("📊 5-CASE BENCHMARK EVALUATION SUMMARY (TA1 vs TA2)")
    print("=" * 80)
    print(f"{'Case':<6} | {'Scenario':<28} | {'TA1 Status':<20} | {'TA2 Negotiation & Hops':<20}")
    print("-" * 80)
    for m in metrics:
        print(f"{m['id']:<6} | {m['name']:<28} | {m['ta1_status'][:20]:<20} | {m['ta2_status']:<20}")
    print("=" * 80)


def main() -> None:
    print("================================================================")
    print("🚀 TA2 AUTOMATED BENCHMARK & EVIDENCE EVALUATION SUITE")
    print("================================================================")
    run_unit3_evidence()
    run_unit4_evidence()
    run_5_test_cases_evaluation()
    print("\n✅ All evidence traces successfully generated in:", TRACES_DIR)


if __name__ == "__main__":
    main()
