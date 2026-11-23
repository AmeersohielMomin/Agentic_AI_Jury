# TA2 Project Report: Multi-Agent Study Schedule Optimizer
**Course**: Agentic AI (LY-AIA) | **Topic 8**: Study Schedule Optimizer (Two-Tool Chain Extension)  
**Stack**: Python 3.13, Ollama (`qwen2.5:3b`, `nomic-embed-text`), LangGraph, LangChain v1, ChromaDB, SQLite

---

## 1. System Architecture & Coordination Workflow

The TA2 Study Schedule Optimizer extends the single-agent TA1 tool baseline into a resilient, memory-augmented multi-agent system.

```
       +--------------------------------------------------------------------------+
       |                  Student / Evaluator User Query                          |
       +------------------------------------+-------------------------------------+
                                            |
                                            v
       +--------------------------------------------------------------------------+
       |            U4-3: Input Safety Guardrail (Injection & Bad Data Filter)    |
       +------------------------------------+-------------------------------------+
                                            |
                                            v
       +--------------------------------------------------------------------------+
       |               U4-2: Supervisor Orchestrator (MAX_HOPS=5)                 |
       +--------------------+--------------------------------+--------------------+
                            |                                |
         [Route 1: Assess]  v                                v  [Route 2: Plan]
       +-------------------------------+   +--------------------------------------+
       | Readiness Diagnostician Agent |   | Workload Negotiator Agent            |
       | - Evaluates Syllabus Coverage |   | - Calculates Daily Study Hours       |
       | - U3-4: check_exam_readiness  |   | - U3-4: hours_needed_per_day         |
       | - U3-3: Chroma RAG Guidelines |   | - U3-2: SQLite Profile Memory        |
       +---------------+---------------+   +------------------+-------------------+
                       |                                      |
                       +---------------->    <----------------+
                               [Multi-Agent Negotiation]
                                            |
                                            v
       +--------------------------------------------------------------------------+
       |              U4-3: Human Oversight Node (Approve vs Reject)              |
       +------------------------------------+-------------------------------------+
                                            |
                                            v
       +--------------------------------------------------------------------------+
       |                       Final Synthesized Schedule Plan                    |
       +--------------------------------------------------------------------------+
```

---

## 2. Multi-Agent Role Specifications (U4-1: 5-Field Spec)

| Field | Agent 1: Readiness Diagnostician | Agent 2: Workload Planner & Negotiator | Agent 3: Supervisor Orchestrator |
| :--- | :--- | :--- | :--- |
| **1. Name** | `readiness_diagnostician` | `workload_planner` | `supervisor_agent` |
| **2. Goal** | Evaluate syllabus readiness against 80% benchmark; retrieve course difficulty guidelines. | Compute required daily hours, check against student fatigue limits, and negotiate realistic pacing. | Decompose student requests, route across specialist agents, enforce hop limits, and coordinate human oversight. |
| **3. Tools** | `check_exam_readiness`, `StudyGuidelinesRAG` (Chroma). | `hours_needed_per_day`, `SQLiteProfileStore` (SQLite). | State routing, `MAX_HOPS` counter, `HumanOversightNode`. |
| **4. Inputs / Outputs** | **In**: `topics_covered`, `total_topics`, subject.<br>**Out**: `readiness_percentage`, `rag_context`, proposal. | **In**: `remaining_topics`, `days_left`, user profile.<br>**Out**: `hours_per_day`, counter-bid, negotiation status. | **In**: Full `AgentState`.<br>**Out**: Routed transitions, final unified plan. |
| **5. Limits** | Does not allocate calendar study hours or track personal student stamina. | Cannot alter curriculum requirements or certify readiness independently. | Strictly capped at `MAX_HOPS=5` to prevent circular execution loops; cannot alter tool math. |

---

## 3. Required TA2 Component Checklist & Evidence Pointers

| Component ID | Unit | What Was Implemented | Verifiable Evidence Pointer |
| :--- | :---: | :--- | :--- |
| **U3-1: Short-term memory** | 3 | LangGraph checkpointer with `thread_id` retaining multi-turn context; contrast against stateless amnesia. | `traces/u3_1_short_term_memory.txt` |
| **U3-2: Long-term memory** | 3 | SQLite key-value store partitioned by `(user_id, "profile")`; verified survival across process kill and restart. | `traces/u3_2_long_term_memory.txt` |
| **U3-3: Chroma RAG** | 3 | Chroma vector DB indexed with `nomic-embed-text` across 8 chunks; grounded refusal (*"I don't know"*) on out-of-scope query. | `traces/u3_3_rag_k1_vs_k3.txt` |
| **U3-4: Tool failure handling**| 3 | Defensive failure routing wrapping both TA1 tools; catches zero-days, negative counts, and excessive loads. | `traces/u3_4_tool_failure.txt` |
| **U4-1: Role design** | 4 | 5-field explicit specification for Diagnostician, Negotiator, and Supervisor. | Section 2 Table above |
| **U4-2: Coordination** | 4 | Supervisor orchestrator with `MAX_HOPS=5` and multi-agent negotiation / counter-bidding logic. | `traces/u4_2_multiagent_routing.txt` |
| **U4-3: Oversight & Guardrail**| 4 | Dual-path Human-in-the-Loop approval (Approved vs Rejected) + regex prompt injection defense guard. | `traces/u4_3_oversight_hitl.txt`<br>`traces/u4_3_guardrail_injection.txt` |
| **U4-4: Challenge analysis** | 4 | Quantitative comparison of latency, hop costs, and crash vs recovery rates across 5 benchmark scenarios. | `traces/u4_4_challenge_metrics.txt` |
| **EV: 5-Case Evaluation** | 3 & 4| Side-by-side execution of 5 test cases on TA1 baseline vs TA2 multi-agent extension. | `traces/ev_ta1_baseline_5cases.txt`<br>`traces/ev_ta2_extended_5cases.txt` |

---

## 4. Benchmark Evaluation: TA1 Baseline vs TA2 Extension (EV)

The exact same 5 test cases were executed on both the TA1 baseline and the TA2 multi-agent system:

| ID | Test Case Description | TA1 Baseline Output & Behavior | TA2 Multi-Agent Output & Behavior |
| :---: | :--- | :--- | :--- |
| **TC1** | **Fully Prepared Student**<br>(20/20 topics, 5 days, 2h/topic) | `ready (20/20 topics covered, 100.0%)` \| `0.00 study hours per day`<br>*(Single pass, no memory)* | **AGREED (3 hops)**: Identifies 100% readiness, references RAG maintenance policy, plans 0 hrs/day without fatigue warning. |
| **TC2** | **Borderline Readiness**<br>(16/20 topics, 4 days, 1.5h/topic) | `ready (16/20 topics covered, 80.0%)` \| `1.50 study hours per day`<br>*(No student context)* | **AGREED (3 hops)**: Diagnostician flags exact 80% boundary. Negotiator checks Bob's SQLite stamina (8h max); confirms 1.5h/day is safe. |
| **TC3** | **Urgent Catch-up Crunch**<br>(5/12 topics, 2 days, 1.5h/topic) | `not ready yet (5/12, 41.7%)` \| `5.25 study hours per day`<br>*(Naively emits 5.25h)* | **COUNTERED (3 hops)**: Charlie's stamina cap is 3.5h/day. Negotiator rejects 5.25h/day as unsafe burnout, counter-proposes 3.5h cap, triggers HITL oversight. |
| **TC4** | **Extreme Workload Overload**<br>(2/20 topics, 1 day, 2.5h/topic) | `not ready yet (2/20, 10.0%)` \| `45.00 study hours per day`<br>*(Absurd calculation emitted)* | **FAILED / HANDLED (3 hops)**: Failure routing detects 45h/day > 12h biological limit. Explains unfeasibility and recommends institutional deferral. |
| **TC5** | **Boundary / Zero Days Left**<br>(10/20 topics, 0 days, 2h/topic) | **CRASH (`ValueError: days_left must be greater than zero`)**<br>*(Unhandled exception halts system)* | **ROBUST RECOVERY (3 hops)**: Failure routing catches zero-days boundary gracefully; advises immediate summary revision without crash. |

### Analytical Trade-Offs: What Got Better, What Got Worse
- **What Got Better**: TA1 crashed on boundary inputs (TC5: 0 days left) and emitted impossible plans (TC4: 45h/day). TA2 handled both defensively, explaining constraints. Furthermore, TA2 personalizes load via SQLite student stamina and grounds policies in Chroma RAG.
- **What Got Worse**: TA1 arithmetic runs in `< 0.05 ms`. TA2 graph routing, SQLite queries, and Chroma lookups increase execution latency to `~20 - 26 ms`. TA2 also introduces state management complexity compared to TA1's single function call.

---

## 5. Measured Challenge Analysis (U4-4: Latency, Error Propagation & Hops)

| Case ID | Scenario | TA1 Latency (ms) | TA2 Latency (ms) | TA1 Failure Mode | TA2 Recovery / Routing Mode | Hop Count |
| :---: | :--- | :---: | :---: | :--- | :--- | :---: |
| **TC1** | Fully Prepared | 0.02 | 23.15 | None (Correct) | Agreed, Hops within budget | 3 / 5 |
| **TC2** | Borderline | 0.01 | 20.65 | None (Correct) | Agreed, Verified vs SQLite profile | 3 / 5 |
| **TC3** | Urgent Crunch | 0.01 | 20.09 | Unchecked Burnout | Counter-bid triggered, HITL active | 3 / 5 |
| **TC4** | Extreme Overload | 0.01 | 22.96 | Unchecked Math | Caught by Tool Failure Routing | 3 / 5 |
| **TC5** | Zero Days Left | 0.01 | 26.78 | **System Crash (100% Fail)** | **Graceful Catch & Explanation (0% Fail)** | 3 / 5 |

**Key Takeaway**: TA2 trades modest latency overhead (+22 ms) for **100% error containment** on boundary and unfeasible workloads, preventing system crashes and dangerous burnout recommendations.

---

## 6. Limitations and Future Work

1. **3B Model Reasoning Ceiling**: Under local `qwen2.5:3b`, multi-round natural language bidding was stabilized using deterministic state contracts in LangGraph to avoid syntax drift.
2. **Dynamic Calendar Integration**: Future work will integrate Google Calendar / iCal APIs to map study blocks directly into students' free calendar slots.

---

## 7. Viva Defense Preparation (Likely Jury Questions & Answers)

- **Q1: What in the model's response tells you it decided it only needed one tool this time?**  
  *Answer*: In TA1, inspecting the `tool_calls` field of `AIMessage` reveals whether the model emitted requests for one tool or two. For a single-tool question, `tool_calls` contains only `readiness_tool`. The subsequent message sequence receives only one `ToolMessage` and immediately transitions to the final answer without invoking `hours_needed_per_day`.

- **Q2: How do you prevent infinite negotiation loops between the Diagnostician and Negotiator?**  
  *Answer*: We enforce a hard `MAX_HOPS = 5` ceiling in the Supervisor Orchestrator. Every agent execution increments `hop_count`. If consensus is not reached within 5 hops, the supervisor diverts flow to `hop_limit_reached` and alerts the user.

- **Q3: How do you know Chroma RAG is grounded and not hallucinating?**  
  *Answer*: As shown in `traces/u3_3_rag_k1_vs_k3.txt`, when presented with an unanswerable question outside the academic guidelines (e.g. cafeteria menu or parking fees), the grounded prompt strictly outputs: *"I don't know based on the provided documents."*

- **Q4: How does long-term memory survive process restarts?**  
  *Answer*: The `SQLiteProfileStore` writes student records directly to disk in `student_profiles.sqlite` under namespace `(user_id, "profile")`. In `traces/u3_2_long_term_memory.txt`, the Python process instance was terminated, a new connection was established, and the exact profile was recalled without data loss.

---

## 8. Group Contribution Table

| Member Name | Assigned Module | Contributions & Deliverables |
| :--- | :--- | :--- |
| **Member 1** | **Memory Systems (U3-1, U3-2)** | Implemented LangGraph `MemorySaver` checkpointer with `thread_id` and SQLite persistent store with namespace `(user_id, "profile")`. |
| **Member 2** | **RAG & Tool Handling (U3-3, U3-4)** | Curated 8-chunk institutional guidelines corpus; integrated Chroma vector DB with `nomic-embed-text` and implemented tool failure routing. |
| **Member 3** | **Multi-Agent Roles & Routing (U4-1, U4-2)** | Authored 5-field agent specifications; implemented LangGraph Supervisor Orchestrator with `MAX_HOPS=5` and specialist negotiation protocol. |
| **Member 4** | **Safety, Oversight & Evaluation (U4-3, U4-4, EV)** | Built regex prompt injection guardrail; added human approval oversight node; conducted automated 5-case benchmark evaluation. |
