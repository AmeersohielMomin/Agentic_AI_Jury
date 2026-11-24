"""Readiness Diagnostician Specialist Agent (Unit 4).

Role 1 of 5-field spec:
- Name: readiness_diagnostician
- Goal: Assess syllabus readiness percentage against 80% threshold and retrieve institutional guidelines.
- Tools: check_exam_readiness, StudyGuidelinesRAG
- Inputs / Outputs: (topics_covered, total_topics, subject) -> (readiness_result, rag_context, proposal)
- Limits: Evaluates curriculum readiness and syllabus rules only; does not calendar personal hours.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.state import AgentState
from tools.exam_tools import check_exam_readiness
from tools.rag_tool import StudyGuidelinesRAG


class ReadinessDiagnostician:
    def __init__(self, rag_instance: StudyGuidelinesRAG | None = None) -> None:
        self.rag = rag_instance or StudyGuidelinesRAG()

    def process(self, state: AgentState) -> Dict[str, Any]:
        """Diagnose readiness and formulate initial academic proposal."""
        covered = state.get("topics_covered", 0)
        total = state.get("total_topics", 20)
        subject = state.get("subject_name", "AI Exam")

        # Step 1: Run deterministic readiness tool with failure routing
        readiness = check_exam_readiness(covered, total)
        
        # Step 2: Retrieve relevant curriculum guidelines from Chroma RAG
        rag_query = f"readiness benchmark pass threshold topic weightage for {subject}"
        retrieved_docs = self.rag.retrieve(rag_query, k=2)
        rag_summary = " ".join([d.page_content.split("\n")[0] for d in retrieved_docs])

        # Step 3: Formulate initial proposal for the student
        remaining = max(0, total - covered)
        if readiness.status == "SUCCESS":
            if readiness.raw_value >= 80.0:
                proposal = (
                    f"[Diagnostician Proposal]: Student has achieved {readiness.raw_value:.1f}% coverage. "
                    f"Readiness Status: READY. Only light maintenance revision is required."
                )
            else:
                proposal = (
                    f"[Diagnostician Proposal]: Student is at {readiness.raw_value:.1f}% coverage (Deficit: {80.0 - readiness.raw_value:.1f}%). "
                    f"Must complete at least {remaining} remaining topics to achieve institutional certification. "
                    f"Policy requirement: {rag_summary}"
                )
        else:
            proposal = f"[Diagnostician Error]: {readiness.output}"

        messages = list(state.get("messages", []))
        messages.append({
            "sender": "readiness_diagnostician",
            "content": proposal,
            "tool_output": readiness.output,
        })

        return {
            "readiness_result": {
                "status": readiness.status,
                "output": readiness.output,
                "percentage": readiness.raw_value,
            },
            "rag_context": rag_summary,
            "diagnostician_proposal": proposal,
            "messages": messages,
            "hop_count": state.get("hop_count", 0) + 1,
        }
