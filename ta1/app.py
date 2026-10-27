"""Professional Streamlit interface for the Study Schedule Optimizer."""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from study_schedule_optimizer import (
    check_exam_readiness,
    run_agent,
    run_offline_scenario,
)


st.set_page_config(
    page_title="Study Schedule Optimizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .hero { background: linear-gradient(135deg, #102a43, #0f766e);
            padding: 2rem 2.25rem; border-radius: 18px; color: white;
            margin-bottom: 1.5rem; }
    .hero h1 { margin: 0; font-size: 2.35rem; }
    .hero p { margin: .55rem 0 0; color: #d9f4ef; font-size: 1.05rem; }
    .result-card { border: 1px solid #d9e2ec; border-radius: 14px;
                   padding: 1rem 1.15rem; background: #f8fafc; }
    .result-label { color: #52606d; font-size: .82rem; text-transform: uppercase;
                    letter-spacing: .08em; }
    .result-value { color: #102a43; font-size: 1.45rem; font-weight: 700;
                    margin-top: .25rem; }
    .small-muted { color: #627d98; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


SCENARIOS = {
    "Custom inputs": {"topics_covered": 14, "total_topics": 20, "days_left": 3, "hours_per_topic": 2.0},
    "Fully prepared": {"topics_covered": 20, "total_topics": 20, "days_left": 5, "hours_per_topic": 2.0},
    "Borderline readiness": {"topics_covered": 16, "total_topics": 20, "days_left": 4, "hours_per_topic": 1.5},
    "Urgent catch-up": {"topics_covered": 5, "total_topics": 12, "days_left": 2, "hours_per_topic": 1.5},
}


def _card(label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f'<div class="result-card"><div class="result-label">{label}</div>'
        f'<div class="result-value">{value}</div>'
        f'<div class="small-muted">{caption}</div></div>',
        unsafe_allow_html=True,
    )


def _readiness_only_result(covered: int, total: int) -> dict[str, Any]:
    readiness = check_exam_readiness(covered, total)
    return {
        "question": f"I covered {covered} of {total} topics. Am I exam ready?",
        "model": "offline-deterministic",
        "tool_events": [
            {
                "name": "check_exam_readiness",
                "arguments": {"topics_covered": covered, "total_topics": total},
                "result": readiness,
            }
        ],
        "message_trace": [
            {"step": "model", "tool_calls": [{"name": "readiness_tool"}]},
            {"step": "tool", "name": "readiness_tool", "content": readiness},
            {"step": "model", "tool_calls": [], "content": readiness},
        ],
        "final_answer": readiness,
    }


def main() -> None:
    st.markdown(
        '<div class="hero"><h1>📚 Study Schedule Optimizer</h1>'
        '<p>An autonomous multi-tool agent for exam readiness and daily study planning.</p></div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Run settings")
        mode = st.radio(
            "Execution mode",
            ["Ollama agent", "Offline deterministic"],
            index=0,
            help="Ollama mode uses LangChain create_agent(). Offline mode runs the same tools without a model.",
        )
        model_name = st.text_input(
            "Ollama model",
            value=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b"),
            disabled=mode != "Ollama agent",
        )
        st.divider()
        st.caption("Tools registered with the agent")
        st.code("readiness_tool\ndaily_hours_tool", language="text")
        st.caption("UI is optional for the assignment, but useful for a live demonstration.")

    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Student inputs")
        scenario_name = st.selectbox("Load an example", list(SCENARIOS), key="scenario_name")
        preset = SCENARIOS[scenario_name]
        if st.session_state.get("_loaded_scenario") != scenario_name:
            st.session_state["topics_covered"] = preset["topics_covered"]
            st.session_state["total_topics"] = preset["total_topics"]
            st.session_state["days_left"] = preset["days_left"]
            st.session_state["hours_per_topic"] = preset["hours_per_topic"]
            st.session_state["_loaded_scenario"] = scenario_name
        with st.form("optimizer_form"):
            topics_covered = st.number_input(
                "Topics covered", min_value=0, step=1, key="topics_covered"
            )
            total_topics = st.number_input(
                "Total topics", min_value=1, step=1, key="total_topics"
            )
            days_left = st.number_input(
                "Days left", min_value=1, step=1, key="days_left"
            )
            hours_per_topic = st.number_input(
                "Hours required per topic", min_value=0.0,
                step=0.5, key="hours_per_topic"
            )
            analysis_type = st.radio(
                "Analysis requested",
                ["Full schedule analysis", "Readiness check only"],
            )
            submitted = st.form_submit_button(
                "Analyze study plan", type="primary", use_container_width=True
            )

    with right:
        st.subheader("How it works")
        st.markdown(
            "1. The student enters planning data.\n"
            "2. The agent identifies the required tool(s).\n"
            "3. Deterministic Python tools calculate the result.\n"
            "4. The agent returns a concise explanation."
        )
        st.info("The 80% readiness threshold is a project rule, not a medical or academic guarantee.")

    if not submitted:
        st.markdown("Choose an example or enter your own values, then select **Analyze study plan**.")
        return

    if topics_covered > total_topics:
        st.error("Topics covered cannot be greater than total topics.")
        return

    question = (
        f"I covered {topics_covered} of {total_topics} topics. "
        + (
            "Am I exam ready?"
            if analysis_type == "Readiness check only"
            else f"I have {days_left} days left and need {hours_per_topic:g} hours "
            "per topic. Am I exam ready and how many study hours per day should I plan?"
        )
    )

    try:
        if mode == "Offline deterministic":
            if analysis_type == "Readiness check only":
                run = _readiness_only_result(topics_covered, total_topics)
            else:
                run = run_offline_scenario(
                    {
                        "topics_covered": topics_covered,
                        "total_topics": total_topics,
                        "days_left": days_left,
                        "hours_per_topic": hours_per_topic,
                    }
                )
        else:
            run = run_agent(question, model_name)
    except Exception as exc:  # Show actionable UI feedback instead of a traceback.
        st.error(f"The analysis could not be completed: {exc}")
        st.info("Try Offline deterministic mode, or confirm Ollama is running and the model name is correct.")
        return

    st.divider()
    st.subheader("Analysis result")
    percentage = topics_covered / total_topics * 100
    remaining = total_topics - topics_covered
    hours_per_day = remaining * hours_per_topic / days_left
    readiness_value = "Ready" if percentage >= 80 else "Not ready yet"
    metric_one, metric_two, metric_three = st.columns(3)
    with metric_one:
        _card("Readiness", readiness_value, f"{percentage:.1f}% topic coverage")
    with metric_two:
        _card("Topics remaining", str(remaining), f"of {total_topics} total topics")
    with metric_three:
        _card("Study time", f"{hours_per_day:.2f} hrs/day", "based on the entered workload")

    st.success(run["final_answer"])
    st.caption(f"Question processed: {run['question']}")

    with st.expander("View agent and tool trace", expanded=True):
        for item in run.get("message_trace", []):
            if item.get("step") == "model":
                calls = item.get("tool_calls", [])
                if calls:
                    names = ", ".join(call["name"] for call in calls)
                    st.markdown(f"**MODEL →** `{names}`")
                else:
                    st.markdown("**MODEL →** final answer")
            elif item.get("step") == "tool":
                st.markdown(f"**TOOL `{item['name']}` →** {item['content']}")
            if item.get("compatibility_note"):
                st.caption(item["compatibility_note"])

        st.download_button(
            "Download this run as JSON",
            data=json.dumps(run, indent=2),
            file_name="study_schedule_run.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
