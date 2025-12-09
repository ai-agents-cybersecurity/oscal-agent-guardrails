# src/oscal_guardrails/graph.py
from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage

from .models import ToolCall, PolicyDecision
from .agents.planner import planner_node
from .agents.policy_enforcer import policy_enforcer_node
from .agents.responder import responder_node


class GuardState(TypedDict, total=False):
    messages: list[BaseMessage]
    proposed_call: ToolCall
    policy_decision: PolicyDecision
    tool_result: str


def build_graph():
    g = StateGraph(GuardState)

    g.add_node("planner", planner_node)
    g.add_node("policy_enforcer", policy_enforcer_node)
    g.add_node("responder", responder_node)

    g.add_edge(START, "planner")
    g.add_edge("planner", "policy_enforcer")
    g.add_edge("policy_enforcer", "responder")
    g.add_edge("responder", END)

    return g.compile()
