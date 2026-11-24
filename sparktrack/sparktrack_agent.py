#!/usr/bin/env python3
"""SparkTrack Milestone Agent: teams tick completed subtopics, the agent reports."""
from __future__ import annotations

import argparse
import json
import os

PHASES = {
    "Requirements Analysis": ["Problem statement", "Requirements document (SRS)", "Feasibility study"],
    "Design": ["System architecture", "Database / UI design", "Design review with guide"],
    "Implementation": ["Backend module", "Frontend module", "Integration", "Code cleanup"],
    "Testing": ["Test plan", "Unit and integration testing", "Bug fixing"],
    "Maintenance": ["Deployment / handover", "Maintenance plan"],
}
TOTAL = sum(len(v) for v in PHASES.values())  # 15
THRESHOLD = 80.0


# ---------- Plain Python (deterministic) ----------
def readiness_text(completed: int, total: int = TOTAL) -> str:
    if total <= 0 or completed < 0 or completed > total:
        return f"Invalid input: completed={completed}, total={total}."
    pct = completed / total * 100
    status = "ON TRACK (ready)" if pct >= THRESHOLD else "NOT READY yet"
    return f"{status}: {completed}/{total} subtopics done ({pct:.1f}%), {total - completed} remaining."


def hours_text(completed: int, days_left: int, hours_per_subtopic: float, total: int = TOTAL) -> str:
    if days_left <= 0:
        return "Invalid input: days_left must be at least 1."
    if completed < 0 or completed > total or hours_per_subtopic < 0:
        return "Invalid input: check completed subtopics and hours per subtopic."
    remaining = total - completed
    hours = remaining * hours_per_subtopic / days_left
    return (f"{hours:.2f} hours per day needed "
            f"({remaining} remaining subtopics x {hours_per_subtopic:g} h / {days_left} days).")


# ---------- LangChain tools ----------
def _make_tools():
    from langchain.tools import tool

    @tool
    def check_project_readiness(completed_subtopics: int, total_subtopics: int = TOTAL) -> str:
        """Check if a team is on track. Needs the number of completed subtopics (out of 15)."""
        return readiness_text(int(completed_subtopics), int(total_subtopics))

    @tool
    def hours_needed_per_day(completed_subtopics: int, days_left: int,
                             hours_per_subtopic: float, total_subtopics: int = TOTAL) -> str:
        """Hours per day a team must work to finish the remaining subtopics."""
        return hours_text(int(completed_subtopics), int(days_left),
                          float(hours_per_subtopic), int(total_subtopics))

    return [check_project_readiness, hours_needed_per_day]


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content)


def run_agent(question: str, model_name: str = "qwen2.5:1.5b") -> dict:
    from langchain.agents import create_agent
    from langchain_ollama import ChatOllama

    # num_gpu=0 forces CPU (your MX350 has too little memory). Set OLLAMA_NUM_GPU_LAYERS=-1 to allow GPU.
    num_gpu = int(os.getenv("SPARKTRACK_NUM_GPU", "0"))
    model = ChatOllama(model=model_name, temperature=0, num_ctx=2048, num_gpu=num_gpu)
    agent = create_agent(
        model=model,
        tools=_make_tools(),
        system_prompt=(
            "You are the SparkTrack PBL milestone assistant. Use the tools for calculations. "
            "Use check_project_readiness for 'on track' questions. Use hours_needed_per_day "
            "only when days left and hours per subtopic are given. Never invent results. "
            "Answer briefly using the tool output."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    trace = []
    for m in messages:
        t = getattr(m, "type", "")
        if t == "ai":
            calls = getattr(m, "tool_calls", None) or []
            trace.append({"step": "model",
                          "tool_calls": [{"name": c.get("name"), "args": c.get("args", {})} for c in calls],
                          "content": _text(m.content)})
        elif t == "tool":
            trace.append({"step": "tool", "name": getattr(m, "name", "?"), "content": _text(m.content)})
    final = _text(messages[-1].content) if messages else ""
    return {"question": question, "model": model_name, "message_trace": trace, "final_answer": final}


def called_tools(run: dict) -> list[str]:
    return [c["name"] for s in run["message_trace"] if s["step"] == "model" for c in s["tool_calls"]]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true")
    p.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"))
    args = p.parse_args()

    if args.offline:
        print("OFFLINE CHECK (no AI model)")
        print(" ", readiness_text(6))
        print(" ", hours_text(6, 5, 2.0))
        return

    tests = [
        ("Our team has completed 6 of 15 subtopics. Are we on track for submission?",
         ["check_project_readiness"]),
        ("Our team has completed 6 of 15 subtopics, has 5 days left and needs about 2 hours "
         "per subtopic. Are we on track, and how many hours per day must we work?",
         ["check_project_readiness", "hours_needed_per_day"]),
    ]
    runs = []
    for q, expected in tests:
        run = run_agent(q, args.model)
        got = called_tools(run)
        ok = sorted(set(got)) == sorted(expected)
        errors = any("Error" in s.get("content", "") for s in run["message_trace"] if s["step"] == "tool")
        print(f"\nQ: {q}")
        for s in run["message_trace"]:
            if s["step"] == "model" and s["tool_calls"]:
                print("  MODEL -> CALL", s["tool_calls"])
            elif s["step"] == "tool":
                print(f"  TOOL {s['name']} -> {s['content']}")
        print(f"  FINAL: {run['final_answer']}")
        print(f"  CHECK: expected {expected}, got {got} -> {'PASS' if ok and not errors else 'FAIL'}")
        runs.append(run)
    with open("traces.json", "w", encoding="utf-8") as f:
        json.dump(runs, f, indent=2)
    print("\nSaved real trace to traces.json")


if __name__ == "__main__":
    main()