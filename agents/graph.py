"""LangGraph state machine for the AI Courtroom debate flow."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents.nodes import (
    cross_examination_node,
    defense_node,
    judge_node,
    prosecution_node,
    research_node,
)


class CourtroomState(TypedDict, total=False):
    """State flowing through the courtroom pipeline."""

    claim: str
    research: str
    raw_evidence: str
    prosecution_argument: str
    defense_argument: str
    cross_examination: str
    verdict: str
    scores: dict
    stage: str


def build_courtroom_graph() -> StateGraph:
    """Build and compile the courtroom debate graph."""
    graph = StateGraph(CourtroomState)

    # Add nodes (agents)
    graph.add_node("research", research_node)
    graph.add_node("prosecution", prosecution_node)
    graph.add_node("defense", defense_node)
    graph.add_node("cross_examination", cross_examination_node)
    graph.add_node("judge", judge_node)

    # Define the flow: research → prosecution → defense → cross-exam → judge
    graph.set_entry_point("research")
    graph.add_edge("research", "prosecution")
    graph.add_edge("prosecution", "defense")
    graph.add_edge("defense", "cross_examination")
    graph.add_edge("cross_examination", "judge")
    graph.add_edge("judge", END)

    return graph.compile()


def run_trial(claim: str) -> dict[str, Any]:
    """Run a full courtroom trial on a claim. Returns final state."""
    app = build_courtroom_graph()
    result = app.invoke({"claim": claim, "stage": "started"})
    return result
