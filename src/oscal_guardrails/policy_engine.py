# src/oscal_guardrails/policy_engine.py
from __future__ import annotations

from typing import Dict

from .models import PolicyRule, PolicyDecision, ToolCall, Effect
from .policy_loader import load_policy_profile


class PolicyEngine:
    def __init__(self, rules: Dict[str, PolicyRule] | None = None):
        self.rules: Dict[str, PolicyRule] = rules or load_policy_profile()

    def decide(self, call: ToolCall) -> PolicyDecision:
        rule = self.rules.get(call.tool_name)

        if rule is None:
            # Default: deny unknown tools
            return PolicyDecision(
                tool_call=call,
                effect="deny",
                reason=f"No OSCAL policy rule for tool '{call.tool_name}'.",
            )

        return PolicyDecision(
            tool_call=call,
            effect=rule.effect,
            reason=rule.reason,
            control_id=rule.control_id,
        )
