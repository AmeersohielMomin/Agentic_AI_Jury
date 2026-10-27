# Study Schedule Optimizer

## What is included

`study_schedule_optimizer.py` registers these two tools with LangChain's
`create_agent()`:

1. `check_exam_readiness(topics_covered, total_topics)` — ready at 80% or more.
2. `hours_needed_per_day(remaining_topics, days_left, hours_per_topic)` —
   `(remaining_topics × hours_per_topic) ÷ days_left`.

The same agent receives both tools for both questions. The model decides which
tools to call; the Python functions perform the arithmetic deterministically.

## Run it

From the `outputs` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama serve
ollama pull qwen2.5:3b
python study_schedule_optimizer.py --trace-json traces.json
```

The screenshot supplied with this task shows `qwen2.5-coder:3b` installed. If
that is the model available locally, run:

```bash
python study_schedule_optimizer.py --model qwen2.5-coder:3b
```

To verify the tools and expected trace immediately, without installing
anything or starting Ollama:

```bash
python study_schedule_optimizer.py --offline
```

The runner also handles the local `qwen2.5-coder:3b` behavior where the model
prints JSON tool requests as text instead of filling `AIMessage.tool_calls`.
It recognizes those requests, executes the registered Python functions, and
labels the trace with a compatibility note. A model with native tool-calling
support will use the normal LangChain path automatically.

## Question comparison

### One-tool question

> I covered 18 of 20 topics. Am I exam ready?

Expected trace:

```text
MODEL -> readiness_tool
TOOL readiness_tool -> ready (18/20 topics covered, 90.0%).
MODEL -> final answer
```

Only the readiness tool is relevant. The model emits one tool call, receives
one `ToolMessage`, and then emits a final answer. It does not call the daily
hours tool because the question provides no remaining-topic workload or time
budget to calculate.

### Two-tool question

> I covered 14 of 20 topics and have 3 days left. Assuming 2 hours per topic,
> am I exam ready and how many study hours per day should I plan?

Expected trace:

```text
MODEL -> readiness_tool, daily_hours_tool
TOOL readiness_tool -> not ready yet (14/20 topics covered, 70.0%).
TOOL daily_hours_tool -> 4.00 study hours per day (6 remaining topics × 2 hours/topic ÷ 3 days).
MODEL -> final answer
```

The two-tool trace has two tool calls and two tool results before the final
answer. These tools are independent, so a model/provider may request them in
one assistant turn or in separate turns; the important evidence is that both
tool names and both results occur before the final response.

## Jury questions

### 1. What proves the model decided it only needed one tool?

Look at the assistant message's `tool_calls` field and the following message
sequence. In the one-tool run, `tool_calls` contains only `readiness_tool`, the
trace contains only one tool result, and the next assistant message has no
further tool calls (`tool_calls=[]`) before the final answer. The absence of a
`daily_hours_tool` call is meaningful because both tools were registered with
the same agent; it was not hidden from the model.

The final wording alone is weaker evidence. The structured trace is the right
evidence for tool selection.

### 2. How do we add a third tool without confusing the order?

Add a third, single-purpose tool. An executable version is provided in
`three_tool_extension.py`:

```python
def build_daily_plan(remaining_topics: int, days_left: int,
                     hours_per_day: float) -> str:
    """Create a day-by-day plan from a workload and daily study budget."""
    topics_per_day = remaining_topics / days_left
    return (f"Study about {topics_per_day:.1f} topics per day for "
            f"{hours_per_day:.2f} hours per day.")
```

Use explicit orchestration when order is a real dependency:

```python
def three_tool_chain(covered: int, total: int, days: int, hours_per_topic: float):
    # Step 1: establish the current state.
    readiness = check_exam_readiness(covered, total)

    # Step 2: derive the workload from that state.
    remaining = total - covered
    hours = hours_needed_per_day(remaining, days, hours_per_topic)
    hours_value = remaining * hours_per_topic / days

    # Step 3: consume the known result; no model guesswork about ordering.
    plan = build_daily_plan(remaining, days, hours_value)
    return {"readiness": readiness, "hours": hours, "plan": plan}
```

Run the extension with:

```bash
python3 outputs/three_tool_extension.py
```

For a production workflow, put those three steps in a LangGraph state graph
with typed state and edges `readiness -> workload -> plan -> END`. Registering
all three tools with one free-form agent is fine when they are independent; it
is not the right control mechanism when tool B requires tool A's output. An
explicit graph makes dependencies, retries, and the trace order visible and
testable.

## Is a UI required?

No. The assignment asks for a working script and a trace comparison, so a
terminal program is sufficient and is preferable for demonstrating the agent
loop. A UI is an optional presentation layer, not part of the core requirement.

If this becomes a user-facing study planner later, a small Streamlit or Gradio
form could collect covered topics, total topics, days, and hours per topic,
then display the final answer and expandable tool trace. Build that only after
the command-line agent and trace are working.
