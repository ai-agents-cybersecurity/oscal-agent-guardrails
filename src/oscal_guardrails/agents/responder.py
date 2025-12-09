# src/oscal_guardrails/agents/responder.py
from __future__ import annotations

from typing import Dict, Any
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AnyMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from ..config import OPENAI_MODEL
from ..models import PolicyDecision


_llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that must respect the described policy decisions. "
            "Explain clearly to the user what happened: "
            "whether the tool call was allowed or blocked and why, "
            "and provide the best answer you can."
        ),
        (
            "human",
            "User request:\n{request}\n\n"
            "Policy decision:\n{decision_json}\n\n"
            "Tool result:\n{tool_result}\n\n"
            "Now respond to the user."
        ),
    ]
)


def responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state_messages: list[AnyMessage] = state.get("messages", [])
    decision: PolicyDecision = state.get("policy_decision")
    tool_result: str = state.get("tool_result", "")

    user_text = ""
    for m in reversed(state_messages):
        if isinstance(m, HumanMessage):
            user_text = m.content
            break

    decision_json = json.dumps(decision.model_dump(), indent=2)

    prompt_messages = _PROMPT.format_messages(
        request=user_text,
        decision_json=decision_json,
        tool_result=tool_result,
    )
    resp = _llm.invoke(prompt_messages)

    # append AIMessage to conversation
    new_messages = state_messages + [AIMessage(content=resp.content)]
    return {"messages": new_messages}
