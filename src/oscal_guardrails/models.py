# src/oscal_guardrails/models.py
from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel

Effect = Literal["allow", "deny", "needs_approval"]


class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, str]


class PolicyRule(BaseModel):
    tool_name: str
    effect: Effect
    reason: str
    control_id: Optional[str] = None


class PolicyDecision(BaseModel):
    tool_call: ToolCall
    effect: Effect
    reason: str
    control_id: Optional[str] = None
