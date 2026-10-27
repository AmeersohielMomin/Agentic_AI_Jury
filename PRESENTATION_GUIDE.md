# Study Schedule Optimizer — Presentation Guide

## Project objective

Build a small autonomous study-planning agent that can select the right tool
for a student's question. The agent must demonstrate both selective tool use
and a multi-tool chain, then expose the difference in the execution trace.

## 60-second explanation

“This project uses a local Ollama model through LangChain. I registered two
deterministic Python tools: one checks whether topic coverage reaches the 80%
readiness threshold, and the other calculates required study hours per day.
For a readiness-only question, the agent calls only the first tool. For a
combined question, it calls both tools and then synthesizes one answer. The
trace proves which tools were selected; the model is not trusted to perform
the arithmetic itself.”

## Files to show

| File | Purpose |
|---|---|
| `study_schedule_optimizer.py` | Main `create_agent()` implementation and trace runner |
| `three_tool_extension.py` | Explicit ordered three-tool workflow |
| `TRACE_COMPARISON.md` | Detailed trace analysis and jury answers |
| `PRESENTATION_GUIDE.md` | This presentation script and extra examples |
| `requirements.txt` | Python dependencies |
| `traces.json` | Machine-readable output from a live run |
| `app.py` | Optional professional Streamlit UI for live input and trace display |

## Main demonstration

Run from the project folder:

```bash
cd "/Users/ameersohielmomingmail.com/Agentic AI /Jury 1"
.venv/bin/python study_schedule_optimizer.py \
  --model qwen2.5-coder:3b \
  --trace-json traces.json
```

Show these results:

| Question | Expected tool selection | Result |
|---|---|---|
| 18 of 20 topics covered; ready? | `readiness_tool` only | 90%, ready |
| 14 of 20; 3 days; 2 hours/topic | Both tools | 70%, not ready; 4 hours/day |

## Additional examples

Run three extra scenarios with:

```bash
.venv/bin/python study_schedule_optimizer.py \
  --model qwen2.5-coder:3b \
  --examples \
  --trace-json traces.json
```

### Example 1: Fully prepared student

Inputs: 20 of 20 topics, 5 days left, 2 hours/topic.

Expected result:

```text
ready (20/20 topics covered, 100.0%).
0.00 study hours per day.
```

### Example 2: Borderline readiness

Inputs: 16 of 20 topics, 4 days left, 1.5 hours/topic.

Expected result:

```text
ready (16/20 topics covered, 80.0%).
1.50 study hours per day.
```

This demonstrates the exact 80% boundary.

### Example 3: Urgent catch-up plan

Inputs: 5 of 12 topics, 2 days left, 1.5 hours/topic.

Expected result:

```text
not ready yet (5/12 topics covered, 41.7%).
5.25 study hours per day.
```

This demonstrates that the tools also identify an unrealistic workload.

## Three-tool extension

The third tool creates a daily plan after the first two calculations. The
workflow is deliberately ordered:

```text
check readiness
      ↓
calculate remaining-topic workload
      ↓
build daily study plan
```

Run it with:

```bash
.venv/bin/python three_tool_extension.py
```

Use an explicit graph or orchestrator when one tool depends on the output of a
previous tool. Let the agent choose freely only when tools are independent.

## Important implementation note

The installed `qwen2.5-coder:3b` model sometimes prints JSON-shaped tool
requests as text instead of populating native tool-call metadata. The runner
detects that format, executes the registered Python functions, and records the
execution clearly. This keeps the demo reliable on the available local model.
The `--offline` mode is deterministic and does not require Ollama.

## What is not required

A UI is not required for this assignment. The terminal output, saved JSON
trace, and written comparison are sufficient. A UI could be added later as a
presentation layer using Streamlit or Gradio.

The optional Streamlit UI is now included. Launch it with:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

It accepts user inputs, supports example presets, offers readiness-only or
full schedule analysis, displays summary cards, and provides a downloadable
JSON trace.
