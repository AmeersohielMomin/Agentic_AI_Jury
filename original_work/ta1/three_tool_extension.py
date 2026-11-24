#!/usr/bin/env python3
"""Explicitly ordered three-tool extension for the study schedule demo.

This version does not ask an LLM to guess the order. The Python orchestration
enforces: readiness -> daily hours -> daily plan.
"""

from __future__ import annotations

from study_schedule_optimizer import (
    check_exam_readiness,
    hours_needed_per_day,
)


def build_daily_plan(
    remaining_topics: int, days_left: int, hours_per_day: float
) -> str:
    """Create a simple daily plan from workload and available days."""
    if days_left <= 0:
        raise ValueError("days_left must be greater than zero")
    topics_per_day = remaining_topics / days_left
    return (
        f"Study about {topics_per_day:.1f} topics per day for "
        f"{hours_per_day:.2f} hours per day."
    )


def three_tool_chain(
    topics_covered: int,
    total_topics: int,
    days_left: int,
    hours_per_topic: float,
) -> dict[str, str]:
    """Run three dependent steps in an explicit, testable order."""
    # Tool 1: assess current readiness.
    readiness = check_exam_readiness(topics_covered, total_topics)

    # Tool 2: calculate workload using the remaining topics.
    remaining_topics = total_topics - topics_covered
    hours_text = hours_needed_per_day(
        remaining_topics, days_left, hours_per_topic
    )
    hours_value = remaining_topics * hours_per_topic / days_left

    # Tool 3: consume the result from Tool 2.
    plan = build_daily_plan(remaining_topics, days_left, hours_value)
    return {
        "readiness": readiness,
        "hours_needed_per_day": hours_text,
        "daily_plan": plan,
    }


if __name__ == "__main__":
    result = three_tool_chain(
        topics_covered=14,
        total_topics=20,
        days_left=3,
        hours_per_topic=2.0,
    )
    print("Three-tool ordered chain: readiness -> hours -> plan")
    for name, value in result.items():
        print(f"{name}: {value}")
