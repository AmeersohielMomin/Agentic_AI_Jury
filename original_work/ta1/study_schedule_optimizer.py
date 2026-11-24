#!/usr/bin/env python3
"""Study Schedule Optimizer: a two-tool LangChain/Ollama agent demo.

Normal mode uses LangChain's current ``create_agent`` API and a local Ollama
model.  ``--offline`` runs the same deterministic tools without requiring
LangChain or Ollama, which is useful for checking the arithmetic and the
expected trace shape before installing dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable


@dataclass
class ToolEvent:
    """A compact, model-independent record of a tool execution."""

    name: str
    arguments: dict[str, Any]
    result: str


_TOOL_EVENTS: list[ToolEvent] = []

EXTRA_SCENARIOS = [
    {
        "label": "Fully prepared student",
        "topics_covered": 20,
        "total_topics": 20,
        "days_left": 5,
        "hours_per_topic": 2.0,
    },
    {
        "label": "Borderline readiness",
        "topics_covered": 16,
        "total_topics": 20,
        "days_left": 4,
        "hours_per_topic": 1.5,
    },
    {
        "label": "Urgent catch-up plan",
        "topics_covered": 5,
        "total_topics": 12,
        "days_left": 2,
        "hours_per_topic": 1.5,
    },
]


def _reset_trace() -> None:
    _TOOL_EVENTS.clear()


def _record(name: str, arguments: dict[str, Any], result: str) -> str:
    _TOOL_EVENTS.append(ToolEvent(name, arguments, result))
    return result


def check_exam_readiness(topics_covered: int, total_topics: int) -> str:
    """Decide whether the learner is ready based on topic coverage.

    A learner is considered ready when at least 80% of the topics are covered.
    """
    if total_topics <= 0:
        raise ValueError("total_topics must be greater than zero")
    if topics_covered < 0 or topics_covered > total_topics:
        raise ValueError("topics_covered must be between 0 and total_topics")

    percentage = topics_covered / total_topics * 100
    status = "ready" if percentage >= 80 else "not ready yet"
    return _record(
        "check_exam_readiness",
        {"topics_covered": topics_covered, "total_topics": total_topics},
        f"{status} ({topics_covered}/{total_topics} topics covered, {percentage:.1f}%).",
    )


def hours_needed_per_day(
    remaining_topics: int, days_left: int, hours_per_topic: float
) -> str:
    """Calculate the study hours required per day for the remaining topics."""
    if remaining_topics < 0:
        raise ValueError("remaining_topics cannot be negative")
    if days_left <= 0:
        raise ValueError("days_left must be greater than zero")
    if hours_per_topic < 0:
        raise ValueError("hours_per_topic cannot be negative")

    hours = remaining_topics * hours_per_topic / days_left
    return _record(
        "hours_needed_per_day",
        {
            "remaining_topics": remaining_topics,
            "days_left": days_left,
            "hours_per_topic": hours_per_topic,
        },
        f"{hours:.2f} study hours per day ({remaining_topics} remaining topics × "
        f"{hours_per_topic:g} hours/topic ÷ {days_left} days).",
    )


def _make_langchain_tools() -> list[Callable[..., Any]]:
    """Wrap both functions as LangChain tools, importing optional packages lazily."""
    try:
        from langchain.tools import tool
    except ImportError as exc:
        raise RuntimeError(
            "LangChain is not installed. Run `pip install -r requirements.txt`, "
            "or use `--offline` to verify the deterministic demo."
        ) from exc

    @tool
    def readiness_tool(topics_covered: int, total_topics: int) -> str:
        """Check exam readiness from the number of covered and total topics."""
        return check_exam_readiness(topics_covered, total_topics)

    @tool
    def daily_hours_tool(
        remaining_topics: int, days_left: int, hours_per_topic: float
    ) -> str:
        """Calculate required study hours per day for remaining topics."""
        return hours_needed_per_day(remaining_topics, days_left, hours_per_topic)

    return [readiness_tool, daily_hours_tool]


def _content_to_text(content: Any) -> str:
    """Make LangChain content blocks readable in a terminal trace."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") in {"text", "output_text"}:
                    pieces.append(str(block.get("text", block.get("content", ""))))
            else:
                pieces.append(str(block))
        return "".join(pieces)
    return str(content)


def _message_trace(messages: Iterable[Any]) -> list[dict[str, Any]]:
    """Extract the visible model/tool sequence from an agent result."""
    trace: list[dict[str, Any]] = []
    for message in messages:
        message_type = getattr(message, "type", message.__class__.__name__)
        if message_type == "ai":
            calls = getattr(message, "tool_calls", None) or []
            trace.append(
                {
                    "step": "model",
                    "tool_calls": [
                        {
                            "name": call.get("name"),
                            "args": call.get("args", {}),
                        }
                        for call in calls
                    ],
                    "content": _content_to_text(getattr(message, "content", "")),
                }
            )
        elif message_type == "tool":
            trace.append(
                {
                    "step": "tool",
                    "name": getattr(message, "name", "unknown"),
                    "content": _content_to_text(getattr(message, "content", "")),
                }
            )
        else:
            trace.append(
                {
                    "step": message_type,
                    "content": _content_to_text(getattr(message, "content", "")),
                }
            )
    return trace


def _extract_json_tool_requests(text: str) -> list[dict[str, Any]]:
    """Read JSON tool requests emitted as text by some local Ollama models.

    Native tool-capable models populate ``AIMessage.tool_calls``. Some smaller
    local models instead print one JSON object per requested tool. This parser
    lets the demo execute those requests while preserving a visible trace.
    """
    decoder = json.JSONDecoder()
    requests: list[dict[str, Any]] = []
    position = 0
    while position < len(text):
        try:
            start = text.index("{", position)
        except ValueError:
            break
        try:
            value, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            position = start + 1
            continue
        if isinstance(value, dict) and "name" in value:
            requests.append(value)
        position = start + end
    return requests


def _execute_text_tool_requests(
    requests: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Execute serialized tool requests and return a normalized trace."""
    name_map = {
        "check exam readiness": ("readiness_tool", check_exam_readiness),
        "check_exam_readiness": ("readiness_tool", check_exam_readiness),
        "readiness_tool": ("readiness_tool", check_exam_readiness),
        "hours needed per day": ("daily_hours_tool", hours_needed_per_day),
        "hours_needed_per_day": ("daily_hours_tool", hours_needed_per_day),
        "daily_hours_tool": ("daily_hours_tool", hours_needed_per_day),
    }
    trace: list[dict[str, Any]] = [{
        "step": "model",
        "tool_calls": [],
        "compatibility_note": (
            "The model emitted JSON tool requests as text; the runner executed "
            "the registered Python tools explicitly."
        ),
    }]
    results: list[str] = []
    call_names: list[str] = []
    for request in requests:
        raw_name = str(request.get("name", "")).strip().lower()
        if raw_name not in name_map:
            continue
        tool_name, function = name_map[raw_name]
        arguments = request.get("arguments", request.get("args", {}))
        if not isinstance(arguments, dict):
            continue
        result = function(**arguments)
        call_names.append(tool_name)
        results.append(result)
        trace.append({"step": "tool", "name": tool_name, "content": result})

    if not results:
        return [], ""
    trace[0]["tool_calls"] = [{"name": name} for name in call_names]
    answer = " ".join(results)
    trace.append({"step": "model", "tool_calls": [], "content": answer})
    return trace, answer


def run_agent(question: str, model_name: str) -> dict[str, Any]:
    """Run one question through an agent that has both tools registered."""
    try:
        from langchain.agents import create_agent
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise RuntimeError(
            "Normal mode needs LangChain and langchain-ollama. "
            "Run `pip install -r requirements.txt`."
        ) from exc

    _reset_trace()
    model = ChatOllama(model=model_name, temperature=0)
    agent = create_agent(
        model=model,
        tools=_make_langchain_tools(),
        system_prompt=(
            "You are a study schedule assistant. Use the registered tools when "
            "the question asks for their calculations. Do not invent tool results. "
            "Call only the tools needed, then give a concise answer with the result."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    final_message = messages[-1] if messages else None
    message_trace = _message_trace(messages)
    final_answer = _content_to_text(
        getattr(final_message, "content", "") if final_message else ""
    )

    # qwen2.5-coder:3b can serialize tool calls as ordinary JSON text instead
    # of using AIMessage.tool_calls. Execute that format so the demo still
    # produces a real, inspectable tool execution trace on this local setup.
    has_native_tool_result = any(item["step"] == "tool" for item in message_trace)
    if not has_native_tool_result:
        compatibility_trace, compatibility_answer = _execute_text_tool_requests(
            _extract_json_tool_requests(final_answer)
        )
        if compatibility_trace:
            message_trace = compatibility_trace
            final_answer = compatibility_answer

    return {
        "question": question,
        "model": model_name,
        "tool_events": [asdict(event) for event in _TOOL_EVENTS],
        "message_trace": message_trace,
        "final_answer": final_answer,
    }


def run_offline(question_kind: str) -> dict[str, Any]:
    """Produce a deterministic expected trace without calling an LLM."""
    _reset_trace()
    if question_kind == "one-tool":
        question = "I covered 18 of 20 topics. Am I exam ready?"
        answer = check_exam_readiness(18, 20)
        return {
            "question": question,
            "model": "offline-deterministic",
            "tool_events": [asdict(event) for event in _TOOL_EVENTS],
            "message_trace": [
                {"step": "model", "tool_calls": [{"name": "readiness_tool"}]},
                {"step": "tool", "name": "readiness_tool", "content": answer},
                {"step": "model", "tool_calls": [], "content": answer},
            ],
            "final_answer": answer,
        }

    question = (
        "I covered 14 of 20 topics and have 3 days left. Assuming 2 hours per "
        "topic, am I exam ready and how many study hours per day should I plan?"
    )
    readiness = check_exam_readiness(14, 20)
    hours = hours_needed_per_day(6, 3, 2.0)
    return {
        "question": question,
        "model": "offline-deterministic",
        "tool_events": [asdict(event) for event in _TOOL_EVENTS],
        "message_trace": [
            {
                "step": "model",
                "tool_calls": [
                    {"name": "readiness_tool"},
                    {"name": "daily_hours_tool"},
                ],
            },
            {"step": "tool", "name": "readiness_tool", "content": readiness},
            {"step": "tool", "name": "daily_hours_tool", "content": hours},
            {
                "step": "model",
                "tool_calls": [],
                "content": f"{readiness} {hours}",
            },
        ],
        "final_answer": f"{readiness} {hours}",
    }


def run_offline_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Run an additional example deterministically for repeatable demos."""
    _reset_trace()
    covered = scenario["topics_covered"]
    total = scenario["total_topics"]
    days = scenario["days_left"]
    hours_per_topic = scenario["hours_per_topic"]
    remaining = total - covered
    question = (
        f"I covered {covered} of {total} topics, have {days} days left, and "
        f"need {hours_per_topic:g} hours per topic. Am I ready, and how many "
        "hours per day should I study?"
    )
    readiness = check_exam_readiness(covered, total)
    hours = hours_needed_per_day(remaining, days, hours_per_topic)
    return {
        "question": question,
        "model": "offline-deterministic",
        "tool_events": [asdict(event) for event in _TOOL_EVENTS],
        "message_trace": [
            {
                "step": "model",
                "tool_calls": [
                    {"name": "readiness_tool"},
                    {"name": "daily_hours_tool"},
                ],
            },
            {"step": "tool", "name": "readiness_tool", "content": readiness},
            {"step": "tool", "name": "daily_hours_tool", "content": hours},
            {
                "step": "model",
                "tool_calls": [],
                "content": f"{readiness} {hours}",
            },
        ],
        "final_answer": f"{readiness} {hours}",
    }


def _print_run(label: str, run: dict[str, Any]) -> None:
    print(f"\n=== {label} ===")
    print(f"Question: {run['question']}")
    print("Trace:")
    for item in run["message_trace"]:
        if item["step"] == "model":
            calls = item.get("tool_calls", [])
            if calls:
                print("  MODEL -> " + ", ".join(call["name"] for call in calls))
            else:
                print("  MODEL -> final answer")
        elif item["step"] == "tool":
            print(f"  TOOL {item['name']} -> {item['content']}")
    print(f"Answer: {run['final_answer']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="run deterministic traces without LangChain/Ollama",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        help="Ollama model name (default: qwen2.5:3b)",
    )
    parser.add_argument(
        "--trace-json",
        help="optional path for saving both run traces as JSON",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="run three additional study-planning scenarios",
    )
    args = parser.parse_args()

    if args.offline:
        one_tool = run_offline("one-tool")
        two_tool = run_offline("two-tool")
    else:
        one_tool = run_agent(
            "I covered 18 of 20 topics. Am I exam ready?", args.model
        )
        two_tool = run_agent(
            "I covered 14 of 20 topics and have 3 days left. Assuming 2 hours "
            "per topic, am I exam ready and how many study hours per day should "
            "I plan?",
            args.model,
        )

    _print_run("ONE-TOOL QUESTION", one_tool)
    _print_run("TWO-TOOL QUESTION", two_tool)
    extra_runs: dict[str, dict[str, Any]] = {}
    if args.examples:
        for scenario in EXTRA_SCENARIOS:
            if args.offline:
                example_run = run_offline_scenario(scenario)
            else:
                covered = scenario["topics_covered"]
                total = scenario["total_topics"]
                days = scenario["days_left"]
                hours_per_topic = scenario["hours_per_topic"]
                question = (
                    f"I covered {covered} of {total} topics, have "
                    f"{days} days left, and need {hours_per_topic:g} "
                    "hours per topic. "
                    "Am I ready, and how many hours per day should I study?"
                )
                example_run = run_agent(question, args.model)
            extra_runs[scenario["label"]] = example_run
            _print_run(scenario["label"].upper(), example_run)
    if args.trace_json:
        with open(args.trace_json, "w", encoding="utf-8") as handle:
            json.dump(
                {"one_tool": one_tool, "two_tool": two_tool, "examples": extra_runs},
                handle,
                indent=2,
            )
        print(f"\nSaved trace JSON to {args.trace_json}")


if __name__ == "__main__":
    main()
