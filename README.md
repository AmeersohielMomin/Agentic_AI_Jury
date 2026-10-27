# Agentic AI Jury: Study Schedule Optimizer (Topic 8)

Autonomous multi-agent system and deterministic tool-calling framework for exam readiness assessment and dynamic study workload scheduling.

Built for **Course: Agentic AI (LY-AIA)** | **Topic 8: Study Schedule Optimizer**.

---

## 📌 Overview

This repository contains both iterations of the **Study Schedule Optimizer**:
1. **TA1 Baseline**: A single-agent deterministic tool selection and chaining system (LangChain, Ollama).
2. **TA2 Multi-Agent System**: An enterprise-grade, memory-augmented multi-agent pipeline (LangGraph, ChromaDB, SQLite, Ollama) featuring human-in-the-loop oversight, guardrails, and role negotiation.

---

## 🗂️ Repository Structure

```
├── README.md                                # Root documentation & overview
├── requirements.txt                         # TA1 Python dependencies
├── report.md                                # Comprehensive TA2 academic report
├── report.pdf                               # PDF version of TA2 report
├── report.tex                               # LaTeX source for report
├── PRESENTATION_GUIDE.md                    # 60-second elevator pitch & jury demo guide
├── TRACE_COMPARISON.md                      # Detailed tool trace analysis
├── Study_Schedule_Optimizer_Presentation.pptx # Presentation deck
├── study_schedule_optimizer.py              # TA1 main agent & trace runner
├── three_tool_extension.py                  # TA1 3-tool workflow extension
├── app.py                                   # TA1 Streamlit interface
├── traces.json                              # Machine-readable TA1 execution traces
│
├── ta1/                                     # Isolated TA1 baseline package
│   ├── study_schedule_optimizer.py
│   ├── three_tool_extension.py
│   ├── app.py
│   ├── traces.json
│   ├── requirements.txt
│   ├── PRESENTATION_GUIDE.md
│   └── TRACE_COMPARISON.md
│
├── ta2/                                     # TA2 Multi-Agent Architecture
│   ├── README.md                            # Detailed TA2 technical guide
│   ├── requirements.txt                     # TA2 Python dependencies
│   ├── main.py                              # TA2 CLI pipeline entrypoint
│   ├── app_ta2.py                           # TA2 Live Jury Streamlit UI
│   ├── run_all_evaluations.py               # 5-case benchmark evaluation suite
│   ├── agents/                              # Multi-agent LangGraph graph & state
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── supervisor.py
│   │   ├── diagnostician.py
│   │   └── workload_planner.py
│   ├── guardrails/                          # Prompt injection & input validation
│   │   └── input_guard.py
│   ├── memory/                              # U3-1 short-term & U3-2 long-term memory
│   │   ├── short_term.py
│   │   └── long_term.py
│   ├── database/                            # Persistent stores (SQLite & Chroma)
│   │   ├── profile_store.py
│   │   └── seed_store.py
│   ├── tools/                               # U3-3 Chroma RAG & U3-4 deterministic tools
│   │   ├── rag_tool.py
│   │   └── exam_tools.py
│   └── corpus/                              # Grounded guidelines corpus for RAG
│       └── exam_guidelines.md
│
└── traces/                                  # Evidence logs & evaluation traces
    ├── ev_ta1_baseline_5cases.txt
    ├── ev_ta2_extended_5cases.txt
    ├── u3_1_short_term_memory.txt
    ├── u3_2_long_term_memory.txt
    ├── u3_3_rag_k1_vs_k3.txt
    ├── u3_4_tool_failure.txt
    ├── u4_2_multiagent_routing.txt
    ├── u4_3_guardrail_injection.txt
    ├── u4_3_oversight_hitl.txt
    └── u4_4_challenge_metrics.txt
```

---

## ⚡ Quickstart

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- [Ollama](https://ollama.ai) installed and running locally
- Pull required Ollama models:
  ```bash
  ollama pull qwen2.5:3b
  ollama pull nomic-embed-text
  ```

### 2. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r ta2/requirements.txt
```

---

## 🚀 Running the Project

### TA1: Single-Agent Baseline
- **Run the agent CLI (offline mode)**:
  ```bash
  python study_schedule_optimizer.py --offline
  ```
- **Run with local Ollama**:
  ```bash
  python study_schedule_optimizer.py --model qwen2.5:3b --trace-json traces.json
  ```
- **Launch TA1 Streamlit UI**:
  ```bash
  streamlit run app.py
  ```

### TA2: Multi-Agent System
- **Run the complete pipeline**:
  ```bash
  python ta2/main.py --scenario borderline
  ```
- **Run full benchmark suite (5 cases TA1 vs TA2)**:
  ```bash
  python ta2/run_all_evaluations.py
  ```
- **Launch TA2 Interactive Jury UI**:
  ```bash
  streamlit run ta2/app_ta2.py
  ```

---

## 📊 Evaluation & Traces

Evidence traces validating each requirement are stored in [`traces/`](./traces):
- `ev_ta1_baseline_5cases.txt`: Baseline TA1 evaluation across 5 canonical cases.
- `ev_ta2_extended_5cases.txt`: Extended TA2 multi-agent evaluation.
- `u3_1_short_term_memory.txt`: Thread-based session memory validation.
- `u3_2_long_term_memory.txt`: SQLite cross-session profile persistence.
- `u3_3_rag_k1_vs_k3.txt`: Chroma RAG grounded retrieval comparison.
- `u3_4_tool_failure.txt`: Defensive arithmetic & error handling.
- `u4_2_multiagent_routing.txt`: Supervisor routing & max hop constraints.
- `u4_3_guardrail_injection.txt`: Input injection refusal and sanitization.
- `u4_3_oversight_hitl.txt`: Human-in-the-loop review trace.
- `u4_4_challenge_metrics.txt`: Latency, hop count, and recovery benchmarks.
