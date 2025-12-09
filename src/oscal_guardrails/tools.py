# src/oscal_guardrails/tools.py
from __future__ import annotations

from typing import Dict


def read_public_file(path: str) -> str:
    # Demo behavior
    return f"[PUBLIC CONTENT] Pretend we read file at {path}."


def read_secret_file(path: str) -> str:
    # In real life, this would be dangerous, so policy should guard it.
    return f"[SECRET CONTENT] Pretend we read HIGHLY SENSITIVE file at {path}."


def exfiltrate_data(destination: str) -> str:
    # Always unsafe.
    return f"Attempted to exfiltrate data to {destination} (this should never run!)."


TOOL_REGISTRY = {
    "read_public_file": read_public_file,
    "read_secret_file": read_secret_file,
    "exfiltrate_data": exfiltrate_data,
}


def execute_tool(tool_name: str, args: Dict[str, str]) -> str:
    fn = TOOL_REGISTRY.get(tool_name)
    if not fn:
        return f"[ERROR] Tool '{tool_name}' not found."
    return fn(**args)
