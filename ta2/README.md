# TA2 Multi-Agent Study Schedule Optimizer (Topic 8)

Autonomous multi-agent system extending the TA1 baseline with **Unit 3 (Memory, Tools, RAG)** and **Unit 4 (Multi-Agent Systems & Safety)**.

---

## ⚡ Quickstart (One Command Run)

To run the complete multi-agent pipeline with one command:

```bash
python ta2/main.py --scenario borderline
```

To run all automated benchmarks, generate all evidence traces, and evaluate the 5 test cases on TA1 vs TA2:

```bash
python ta2/run_all_evaluations.py
```

To launch the interactive **Live Jury Demo Streamlit UI**:

```bash
streamlit run ta2/app_ta2.py
```

---

## 🏗️ Architecture & Component Overview

```
                                +-----------------------------+
                                |  Student / Evaluator Input  |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
                                |  U4-3: Input Safety Guard   |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
               +--------------->| Supervisor Agent (MAX_HOPS) |<--------------+
               |                +--------------+--------------+               |
               |                               |                              |
               v                               |                              v
+-------------------------------+              |              +-------------------------------+
| Readiness Diagnostician       |              |              | Workload Planner & Negotiator |
| - TA1 check_exam_readiness    |              |              | - TA1 hours_needed_per_day    |
| - U3-3 Chroma RAG Guidelines  |              |              | - U3-2 SQLite Profile Memory  |
+-------------------------------+              |              +-------------------------------+
                                               v
                                +-----------------------------+
                                |  U4-3: Human Oversight Node |
                                |  (Approved / Rejected Path) |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
                                |  Final Synthesized Schedule |
                                +-----------------------------+
```

---

## 📋 Required TA2 Components Implemented

| ID | Component | Implementation | Evidence Pointer |
| :--- | :--- | :--- | :--- |
| **U3-1** | **Short-Term Memory** | LangGraph checkpointer with `thread_id` tracking multi-turn schedule modifications. | `traces/u3_1_short_term_memory.txt` |
| **U3-2** | **Long-Term Memory** | SQLite persistent store with namespace `(user_id, "profile")` surviving process restarts. | `traces/u3_2_long_term_memory.txt` |
| **U3-3** | **Chroma RAG** | Chroma vector store with `nomic-embed-text` embeddings across 8+ chunks; grounded prompt returning *"I don't know"*. | `traces/u3_3_rag_k1_vs_k3.txt` |
| **U3-4** | **Tool & Failure Handling** | Preserves TA1 tools with defensive failure routing for boundary & arithmetic errors. | `traces/u3_4_tool_failure.txt` |
| **U4-1** | **Role Design** | 5-field specification (Name, Goal, Tools, Inputs/Outputs, Limits) for 3 agents. | Table in `report.md` |
| **U4-2** | **Coordination** | Supervisor router enforcing `MAX_HOPS=5` with specialist negotiation & counter-bidding. | `traces/u4_2_multiagent_routing.txt` |
| **U4-3** | **Oversight & Guardrails** | Human approval step (Approved vs Rejected paths) and prompt injection guard. | `traces/u4_3_oversight_hitl.txt` & `traces/u4_3_guardrail_injection.txt` |
| **U4-4** | **Challenge Analysis** | Quantitative benchmark measuring latency, error recovery, and hop efficiency. | `traces/u4_4_challenge_metrics.txt` |
| **EV** | **Evaluation** | 5 standardized benchmark cases executed side-by-side on TA1 baseline vs TA2. | `traces/ev_ta1_baseline_5cases.txt` & `traces/ev_ta2_extended_5cases.txt` |

---

## 💾 Database Seed & Re-initialization

The SQLite student profile store is automatically created and seeded. To re-seed manually:

```bash
python ta2/database/seed_store.py
```
