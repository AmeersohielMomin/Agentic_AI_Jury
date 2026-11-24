"""Short-term conversational memory with LangGraph checkpointer and thread_id.

Implements U3-1:
- State graph with MemorySaver / SqliteSaver checkpointer
- Multi-turn conversation where Turn 2 depends on Turn 1 parameters
- Contrast demo: With Memory (preserves context) vs Without Memory (shows amnesia)
"""

from __future__ import annotations

import os
from typing import Annotated, Any, Dict, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_ollama import ChatOllama

# Define conversational state
class ChatState(TypedDict):
    messages: list[BaseMessage]


def create_conversational_agent(use_checkpointer: bool = True):
    llm = ChatOllama(model="qwen2.5:3b", temperature=0)

    def chatbot_node(state: ChatState) -> ChatState:
        history = state["messages"]
        system_instruction = (
            "You are a study schedule assistant. Maintain continuous awareness of all prior "
            "topics, covered counts, and exam days mentioned earlier in the conversation. "
            "If the user asks a follow-up change like 'what if I have 2 more days?', reuse "
            "the previously established numbers to compute the updated schedule."
        )
        response = llm.invoke([HumanMessage(content=system_instruction)] + history)
        return {"messages": history + [response]}

    builder = StateGraph(ChatState)
    builder.add_node("chatbot", chatbot_node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    if use_checkpointer:
        memory = MemorySaver()
        return builder.compile(checkpointer=memory)
    else:
        return builder.compile()


def run_short_term_memory_demo() -> Dict[str, Any]:
    turn1_text = (
        "I am preparing for the Machine Learning exam. I have covered 12 out of 20 topics "
        "and have 4 days left. At 2 hours per topic, what is my schedule?"
    )
    turn2_text = "What if the exam is postponed by 2 more days? Recalculate my daily hours."

    # --- RUN WITH MEMORY ---
    agent_with_mem = create_conversational_agent(use_checkpointer=True)
    config = {"configurable": {"thread_id": "study_session_101"}}

    turn1_res = agent_with_mem.invoke(
        {"messages": [HumanMessage(content=turn1_text)]}, config=config
    )
    turn2_res = agent_with_mem.invoke(
        {"messages": turn1_res["messages"] + [HumanMessage(content=turn2_text)]},
        config=config,
    )

    trace_with_memory = {
        "turn1_user": turn1_text,
        "turn1_ai": turn1_res["messages"][-1].content,
        "turn2_user": turn2_text,
        "turn2_ai": turn2_res["messages"][-1].content,
    }

    # --- RUN WITHOUT MEMORY (Amnesia Demonstration) ---
    agent_without_mem = create_conversational_agent(use_checkpointer=False)

    # Turn 1 executed in isolation
    no_mem_turn1 = agent_without_mem.invoke(
        {"messages": [HumanMessage(content=turn1_text)]}
    )
    # Turn 2 executed in isolation without previous message context (simulating stateless loss)
    no_mem_turn2 = agent_without_mem.invoke(
        {"messages": [HumanMessage(content=turn2_text)]}
    )

    trace_without_memory = {
        "turn1_user": turn1_text,
        "turn1_ai": no_mem_turn1["messages"][-1].content,
        "turn2_user": turn2_text,
        "turn2_ai": no_mem_turn2["messages"][-1].content,
    }

    return {
        "with_memory": trace_with_memory,
        "without_memory": trace_without_memory,
    }


if __name__ == "__main__":
    print("=== Running Short-Term Memory Evaluation (U3-1) ===")
    results = run_short_term_memory_demo()

    print("\n" + "=" * 60)
    print("SCENARIO A: WITH SHORT-TERM MEMORY (thread_id='study_session_101')")
    print("=" * 60)
    print(f"Turn 1 User: {results['with_memory']['turn1_user']}")
    print(f"Turn 1 AI:   {results['with_memory']['turn1_ai']}\n")
    print(f"Turn 2 User: {results['with_memory']['turn2_user']}")
    print(f"Turn 2 AI (Context Retained): {results['with_memory']['turn2_ai']}")

    print("\n" + "=" * 60)
    print("SCENARIO B: WITHOUT MEMORY (AMNESIA DEMONSTRATION)")
    print("=" * 60)
    print(f"Turn 1 User: {results['without_memory']['turn1_user']}")
    print(f"Turn 1 AI:   {results['without_memory']['turn1_ai']}\n")
    print(f"Turn 2 User: {results['without_memory']['turn2_user']}")
    print(f"Turn 2 AI (Amnesia / Context Lost): {results['without_memory']['turn2_ai']}")
