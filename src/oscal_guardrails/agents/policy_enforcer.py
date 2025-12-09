# src/oscal_guardrails/agents/policy_enforcer.py
from __future__ import annotations

from typing import Dict, Any

from ..models import ToolCall, PolicyDecision
from ..policy_engine import PolicyEngine
from ..tools import execute_tool


_engine = PolicyEngine()


def policy_enforcer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    call: ToolCall = state.get("proposed_call")
    if call is None:
        return {}

    if call.tool_name == "none":
        # Nothing to do
        decision = PolicyDecision(
            tool_call=call,
            effect="allow",
            reason="No tool needed.",
        )
        return {"policy_decision": decision, "tool_result": ""}

    decision = _engine.decide(call)

    if decision.effect == "allow":
        result = execute_tool(call.tool_name, call.args)
    elif decision.effect == "needs_approval":
        # v0: treat as deny but with different messaging
        result = (
            "[NEEDS APPROVAL] This action requires human approval before execution. "
            "Tool execution skipped."
        )
    else:  # deny
        result = "[DENIED] Tool call blocked by OSCAL policy."

    return {"policy_decision": decision, "tool_result": result}
