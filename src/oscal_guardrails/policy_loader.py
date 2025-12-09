# src/oscal_guardrails/policy_loader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .config import OSCAL_POLICY_PROFILE_PATH
from .models import PolicyRule, Effect


def load_policy_profile(path: str | Path = OSCAL_POLICY_PROFILE_PATH) -> Dict[str, PolicyRule]:
    """
    Load an OSCAL profile (JSON) and extract tool rules from modify.controls[*].props.

    We interpret props:
      - og:tool-name   -> tool_name
      - og:effect      -> allow|deny|needs_approval
      - og:reason      -> human rationale
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    profile = raw.get("profile", raw)
    modify = profile.get("modify", {})
    controls = modify.get("controls", [])

    rules: Dict[str, PolicyRule] = {}

    for c in controls:
        control_id = c.get("control-id")
        props: List[Dict] = c.get("props", [])
        tool_name = None
        effect: Effect = "deny"  # safe default
        reason = "No reason provided."

        for p in props:
            name = p.get("name")
            value = p.get("value")
            if name == "og:tool-name":
                tool_name = value
            elif name == "og:effect":
                if value in {"allow", "deny", "needs_approval"}:
                    effect = value  # type: ignore[assignment]
            elif name == "og:reason":
                reason = value

        if tool_name:
            rules[tool_name] = PolicyRule(
                tool_name=tool_name,
                effect=effect,
                reason=reason,
                control_id=control_id,
            )

    return rules
