"""Study Schedule Optimizer Tools with Robust Failure Routing.

Implements U3-4: Keep TA1 tools, add failure routing so errors are caught
and explained gracefully.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class ToolExecutionResult:
    tool_name: str
    status: str  # "SUCCESS" or "ERROR"
    output: str
    raw_value: Optional[float] = None
    error_type: Optional[str] = None
    suggested_action: Optional[str] = None


def check_exam_readiness(topics_covered: int, total_topics: int) -> ToolExecutionResult:
    """Assess whether a learner is exam ready (benchmark >= 80% coverage).
    
    Includes defensive failure routing for boundary violations.
    """
    # Defensive failure routing
    if not isinstance(topics_covered, (int, float)) or not isinstance(total_topics, (int, float)):
        return ToolExecutionResult(
            tool_name="check_exam_readiness",
            status="ERROR",
            output="Error: topics_covered and total_topics must be numeric values.",
            error_type="TypeError",
            suggested_action="Please provide non-negative integer topic counts.",
        )

    topics_covered = int(topics_covered)
    total_topics = int(total_topics)

    if total_topics <= 0:
        return ToolExecutionResult(
            tool_name="check_exam_readiness",
            status="ERROR",
            output=f"Error: total_topics must be strictly greater than 0 (received {total_topics}).",
            error_type="ZeroOrNegativeTotalTopics",
            suggested_action="Specify a curriculum with at least 1 total topic.",
        )

    if topics_covered < 0:
        return ToolExecutionResult(
            tool_name="check_exam_readiness",
            status="ERROR",
            output=f"Error: topics_covered cannot be negative (received {topics_covered}).",
            error_type="NegativeTopicsCovered",
            suggested_action="Use a valid count of topics covered (>= 0).",
        )

    if topics_covered > total_topics:
        return ToolExecutionResult(
            tool_name="check_exam_readiness",
            status="ERROR",
            output=(
                f"Error: topics_covered ({topics_covered}) exceeds total_topics ({total_topics}). "
                "Coverage cannot be greater than 100%."
            ),
            error_type="OverflowCoverage",
            suggested_action="Verify syllabus syllabus size; clamp topics_covered to total_topics.",
        )

    percentage = (topics_covered / total_topics) * 100.0
    status = "ready" if percentage >= 80.0 else "not ready yet"
    msg = f"{status} ({topics_covered}/{total_topics} topics covered, {percentage:.1f}%)."
    
    return ToolExecutionResult(
        tool_name="check_exam_readiness",
        status="SUCCESS",
        output=msg,
        raw_value=percentage,
    )


def hours_needed_per_day(
    remaining_topics: int,
    days_left: int,
    hours_per_topic: float = 2.0,
    daily_cap: float = 12.0,
) -> ToolExecutionResult:
    """Calculate required study hours per day for the remaining topics.
    
    Includes failure routing for zero days, negative workloads, and unfeasible demands.
    """
    if not isinstance(remaining_topics, (int, float)) or not isinstance(days_left, (int, float)):
        return ToolExecutionResult(
            tool_name="hours_needed_per_day",
            status="ERROR",
            output="Error: remaining_topics and days_left must be numeric values.",
            error_type="TypeError",
            suggested_action="Provide positive numerical parameters.",
        )

    remaining_topics = int(remaining_topics)
    days_left = int(days_left)
    hours_per_topic = float(hours_per_topic)

    if days_left <= 0:
        return ToolExecutionResult(
            tool_name="hours_needed_per_day",
            status="ERROR",
            output=f"Error: days_left must be >= 1 day (received {days_left}). Examination is today or overdue.",
            error_type="ZeroOrNegativeDaysLeft",
            suggested_action="Switch to emergency high-yield revision mode; cannot space hours across zero days.",
        )

    if remaining_topics < 0:
        return ToolExecutionResult(
            tool_name="hours_needed_per_day",
            status="ERROR",
            output=f"Error: remaining_topics cannot be negative (received {remaining_topics}).",
            error_type="NegativeRemainingTopics",
            suggested_action="Set remaining_topics to 0 if all topics are already finished.",
        )

    if hours_per_topic <= 0:
        return ToolExecutionResult(
            tool_name="hours_needed_per_day",
            status="ERROR",
            output=f"Error: hours_per_topic must be greater than zero (received {hours_per_topic}).",
            error_type="InvalidHoursPerTopic",
            suggested_action="Use institutional default of 2.0 hours per topic.",
        )

    total_workload_hours = remaining_topics * hours_per_topic
    hours_per_day = total_workload_hours / days_left

    # Check for unfeasible human limits
    if hours_per_day > daily_cap:
        return ToolExecutionResult(
            tool_name="hours_needed_per_day",
            status="ERROR",
            output=(
                f"Unfeasible Schedule Warning: Required {hours_per_day:.2f} hours/day exceeds "
                f"maximum biological limit of {daily_cap:.1f} hours/day."
            ),
            raw_value=hours_per_day,
            error_type="ExcessiveCognitiveLoad",
            suggested_action="Prioritize high-yield topics only or request exam postponement.",
        )

    msg = (
        f"{hours_per_day:.2f} study hours per day "
        f"({remaining_topics} remaining topics × {hours_per_topic:g} hrs ÷ {days_left} days)."
    )
    return ToolExecutionResult(
        tool_name="hours_needed_per_day",
        status="SUCCESS",
        output=msg,
        raw_value=hours_per_day,
    )
