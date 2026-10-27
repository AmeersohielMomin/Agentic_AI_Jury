"""LangGraph state representation for the Study Schedule Multi-Agent System.

Includes state tracking for multi-agent messages, user profile, negotiation bids,
hop counting (MAX_HOPS limit), human approval, and failure logs.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # Chat message trajectory
    messages: List[Dict[str, Any]]
    
    # User and input parameters
    user_id: str
    student_profile: Dict[str, Any]
    topics_covered: int
    total_topics: int
    days_left: int
    hours_per_topic: float
    subject_name: str
    
    # Agent computation results
    readiness_result: Optional[Dict[str, Any]]
    rag_context: Optional[str]
    workload_result: Optional[Dict[str, Any]]
    
    # Negotiation and coordination (Unit 4)
    diagnostician_proposal: Optional[str]
    negotiator_counter_bid: Optional[str]
    negotiation_status: str  # "PROPOSED", "COUNTERED", "AGREED", "FAILED"
    
    # Hop budget to avoid infinite cycles
    hop_count: int
    max_hops: int
    
    # Human-in-the-loop oversight (U4-3)
    requires_human_approval: bool
    human_decision: Optional[str]  # "APPROVED", "REJECTED", "PENDING"
    human_feedback: Optional[str]
    
    # Final output and routing
    next_node: str
    final_schedule_plan: Optional[str]
    error_log: List[str]
