"""Professional Streamlit UI for TA2 Multi-Agent Study Schedule Optimizer.

Designed for the Live Jury Demo:
- Visualizes Specialist Agent dialogue (Diagnostician & Workload Negotiator)
- Displays Chroma RAG retrieved guidelines
- Interacts with SQLite long-term student profiles
- Interactive Human Oversight (HITL Approval/Rejection)
- Trace & evaluation inspector
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import streamlit as st

# Setup system path
TA2_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TA2_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TA2_DIR))

from agents.graph import build_study_optimizer_graph
from database.profile_store import DEFAULT_DB_PATH, SQLiteProfileStore, get_student_profile
from tools.rag_tool import StudyGuidelinesRAG
from guardrails.input_guard import InputSafetyGuard

st.set_page_config(
    page_title="TA2 Multi-Agent Study Schedule Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a, #0f766e);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .agent-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #3b82f6;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .agent-card-negotiator {
        background: #fdf2f8;
        border: 1px solid #fbcfe8;
        border-left: 5px solid #ec4899;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .supervisor-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #22c55e;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-ready { background: #dcfce7; color: #15803d; }
    .badge-notready { background: #fee2e2; color: #b91c1c; }
    .badge-agreed { background: #e0e7ff; color: #3730a3; }
    .badge-countered { background: #fef3c7; color: #b45309; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin:0; font-size: 2.2rem;">🎓 Study Schedule Optimizer (TA2)</h1>
        <p style="margin:0.5rem 0 0; color: #e0f2fe; font-size: 1.05rem;">
            Autonomous Multi-Agent Architecture • LangGraph Supervisor • SQLite Long-Term Memory • Chroma RAG • Human Oversight
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Student Profile & Configuration
st.sidebar.header("👤 Long-Term Memory (SQLite)")
store = SQLiteProfileStore(DEFAULT_DB_PATH)

profile_options = {
    "student_alice": "Alice Smith (Steady, Max 5h/day)",
    "student_bob": "Bob Vance (High stamina, Max 8h/day)",
    "student_charlie": "Charlie Day (Part-time, Max 3.5h/day)",
}
selected_uid = st.sidebar.selectbox("Select Student Profile:", list(profile_options.keys()), format_func=lambda x: profile_options[x])
profile = get_student_profile(selected_uid)

st.sidebar.markdown(f"**Name:** {profile.get('name')}")
st.sidebar.markdown(f"**Daily Max Stamina:** `{profile.get('daily_max_hours')} hrs/day`")
st.sidebar.markdown(f"**Fatigue Threshold:** `{profile.get('fatigue_threshold')} hrs`")
st.sidebar.markdown(f"**Study Preference:** `{profile.get('study_preference', 'standard')}`")
st.sidebar.info(f"💡 Notes: {profile.get('notes', 'No notes.')}")

st.sidebar.divider()
st.sidebar.header("⚙️ Exam Parameters")
subject = st.sidebar.text_input("Subject / Course Name:", value=profile.get("target_subject", "AI & Agentic Systems"))
total_topics = st.sidebar.number_input("Total Curriculum Topics:", min_value=1, max_value=100, value=20)
topics_covered = st.sidebar.number_input("Topics Covered So Far:", min_value=0, max_value=total_topics, value=14)
days_left = st.sidebar.number_input("Days Left Until Exam:", min_value=1, max_value=60, value=3)
hours_per_topic = st.sidebar.number_input("Hours Needed Per Topic:", min_value=0.5, max_value=10.0, value=2.0, step=0.5)

# Human oversight decision simulation
st.sidebar.divider()
st.sidebar.header("🛡️ Human Oversight (HITL)")
human_decision = st.sidebar.radio(
    "If intensive plan requires approval:",
    ["APPROVED", "REJECTED"],
    help="Demonstrates both paths required by U4-3 oversight.",
)

# Main layout tabs
tab_demo, tab_rag, tab_memory, tab_eval = st.tabs(["🚀 Live Multi-Agent Run", "📚 Chroma RAG Explorer", "🧠 Long-Term Memory", "📊 Evidence & Traces"])

with tab_demo:
    col_run, col_info = st.columns([1, 4])
    with col_run:
        run_btn = st.button("⚡ Optimize Schedule", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Multi-Agent Supervisor orchestrating Diagnostician and Negotiator..."):
            rag = StudyGuidelinesRAG()
            graph = build_study_optimizer_graph(rag_instance=rag)

            initial_state = {
                "messages": [],
                "user_id": selected_uid,
                "student_profile": profile,
                "topics_covered": topics_covered,
                "total_topics": total_topics,
                "days_left": days_left,
                "hours_per_topic": hours_per_topic,
                "subject_name": subject,
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

        # Metrics display
        m1, m2, m3, m4 = st.columns(4)
        pct = (topics_covered / total_topics) * 100.0
        m1.metric("Coverage", f"{pct:.1f}%", f"{topics_covered}/{total_topics} topics")
        status_ready = "READY" if pct >= 80.0 else "DEFICIT"
        m2.metric("Readiness Benchmark", status_ready, "Target: 80%")
        remaining = total_topics - topics_covered
        raw_hours = (remaining * hours_per_topic) / days_left
        m3.metric("Required Daily Pace", f"{raw_hours:.2f} hrs/day", f"{days_left} days left")
        m4.metric("Graph Hops", f"{final_state.get('hop_count', 0)} / 5", "MAX_HOPS budget")

        st.subheader("🤖 Multi-Agent Communication & Negotiation Log")

        # Step 1: Diagnostician Card
        diag_prop = final_state.get("diagnostician_proposal", "")
        st.markdown(
            f"""
            <div class="agent-card">
                <h4>🔍 Agent 1: Readiness Diagnostician</h4>
                <p><strong>Goal:</strong> Validate coverage against 80% certification benchmark and reference RAG policies.</p>
                <div style="background: white; padding: 0.8rem; border-radius: 6px; border: 1px solid #cbd5e1;">
                    {diag_prop}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 2: Workload Negotiator Card
        neg_bid = final_state.get("negotiator_counter_bid", "")
        neg_status = final_state.get("negotiation_status", "")
        st.markdown(
            f"""
            <div class="agent-card-negotiator">
                <h4>⚖️ Agent 2: Workload Planner & Negotiator</h4>
                <p><strong>Goal:</strong> Calculate required hours and negotiate against student SQLite stamina limit (<code>{profile.get('daily_max_hours')} hrs/day</code>).</p>
                <p><strong>Negotiation State:</strong> <span class="badge badge-agreed">{neg_status}</span></p>
                <div style="background: white; padding: 0.8rem; border-radius: 6px; border: 1px solid #fbcfe8;">
                    {neg_bid}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 3: Supervisor Final Synthesis
        st.markdown(
            f"""
            <div class="supervisor-card">
                <h3>👑 Supervisor Orchestration Summary</h3>
                <pre style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #86efac; font-size: 0.95rem;">{final_state.get('final_schedule_plan', '')}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_rag:
    st.subheader("📚 Chroma Vector Store Guidelines (U3-3)")
    st.markdown("Knowledge base indexed with `nomic-embed-text` into 8+ distinct chunks.")
    rag_query = st.text_input("Test Grounded RAG Query:", value="What is the maximum allowed daily study hours before burnout oversight is required?")
    k_val = st.slider("Select k (Number of Chunks):", min_value=1, max_value=5, value=3)
    if st.button("Search Knowledge Base"):
        rag_instance = StudyGuidelinesRAG()
        res = rag_instance.answer_query(rag_query, k=k_val)
        st.markdown(f"**Answer from Grounded LLM:**")
        st.success(res["answer"])
        st.markdown("**Retrieved Chunks:**")
        for idx, doc in enumerate(res["retrieved_chunks"], 1):
            with st.expander(f"Chunk {idx}: {doc['title']}"):
                st.write(doc["content"])

with tab_memory:
    st.subheader("🧠 Long-Term Memory Store (U3-2)")
    st.markdown("Persistent SQLite database storing records partitioned by `(user_id, 'profile')` surviving process restarts.")
    all_users = ["student_alice", "student_bob", "student_charlie"]
    cols = st.columns(len(all_users))
    for i, u in enumerate(all_users):
        with cols[i]:
            u_data = store.get_all(u, "profile")
            st.markdown(f"### `{u}`")
            st.json(u_data)

with tab_eval:
    st.subheader("📊 Evaluation & Traces Explorer")
    st.markdown("Generated traces required by the TA2 SOP:")
    traces_list = list((PROJECT_ROOT / "traces").glob("*.txt"))
    if traces_list:
        selected_trace = st.selectbox("Select Trace to View:", [t.name for t in traces_list])
        trace_file = PROJECT_ROOT / "traces" / selected_trace
        st.code(trace_file.read_text(encoding="utf-8"), language="text")
    else:
        st.info("Run `python ta2/run_all_evaluations.py` to populate all trace files.")
