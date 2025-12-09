[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://langchain-ai.github.io/langgraph/)
[![NIST OSCAL](https://img.shields.io/badge/Docs-NIST%20OSCAL-0a67a3.svg)](https://pages.nist.gov/OSCAL/)
[![OSCAL Content](https://img.shields.io/badge/Repo-oscal--content-ff9800.svg)](https://github.com/usnistgov/oscal-content)
[![LangGraph Docs](https://img.shields.io/badge/Docs-LangGraph-4caf50.svg)](https://langchain-ai.github.io/langgraph/)
[![OSCAL JSON Reference](https://img.shields.io/badge/Reference-OSCAL%20JSON-9c27b0.svg)](https://pages.nist.gov/OSCAL-Reference/)

# oscal-agent-guardrails

Use **OSCAL** as a policy brain to guardrail **LLM agents**.

This repo demonstrates how an OSCAL profile can encode tool-usage policies for an agent, and how a LangGraph workflow can enforce those policies at runtime:

- The **planner agent** turns user intent into a proposed tool call.
- The **policy enforcer** consults an OSCAL profile and decides:
  - `allow` – execute tool,
  - `deny` – block,
  - `needs_approval` – require human approval (v0: simulated).
- The **responder agent** explains to the user what happened and why.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Planner   │────▶│  Policy Enforcer │────▶│  Responder  │
│   (LLM)     │     │  (OSCAL Engine)  │     │   (LLM)     │
└─────────────┘     └──────────────────┘     └─────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ OSCAL Profile │
                    │  (JSON/YAML)  │
                    └───────────────┘
```

## It is pretty cool how it Intercepts Requests

The interception happens via **LangGraph's sequential workflow** — the tool is never called directly. Instead:

```
User Input → Planner → Policy Enforcer → (maybe) Tool → Responder
```

📊 **[View Interactive Concept Map](https://raw.githack.com/ai-agents-cybersecurity/oscal-agent-guardrails/main/map_oscal_agent_guardrails.html)** *(opens in browser)*

---

**Key mechanism:**

1. **Planner** (LLM) outputs a `proposed_call` — just a data structure with `tool_name` + `args`
2. **Policy Enforcer** sits between planner and execution:
   - Looks up the tool in `self.rules` (loaded from OSCAL)
   - Returns `allow`, `deny`, or `needs_approval`
   - Only calls `execute_tool()` if `effect == "allow"`
3. **Responder** explains the outcome to the user

The tool is **never invoked unless explicitly allowed**. This is a "whitelist" pattern — unknown tools are denied by default (line 17-23 in [policy_engine.py](src/oscal_guardrails/policy_engine.py)).

---

## 2. What Else Could Be Controlled by Policy?

Beyond tool usage, OSCAL-based guardrails could control:

| Category | Examples |
|----------|----------|
| **Data access** | PII handling, file path patterns, database queries |
| **Output filtering** | Block responses containing secrets, profanity, code injection |
| **Rate limiting** | Max API calls per minute, token budgets |
| **Model selection** | Force cheaper model for low-risk queries, GPT-4 only for sensitive |
| **Prompt injection defense** | Detect/block jailbreak attempts |
| **Audit logging** | Which actions require logging, retention policies |
| **Human-in-the-loop** | Escalation thresholds, approval workflows |
| **Context window** | Max history length, what gets remembered |
| **External comms** | Allowed domains, email recipients, webhook destinations |
| **Code execution** | Sandboxing rules, allowed languages, timeout limits |

The OSCAL structure (controls → parameters → assessments) maps naturally to these — each becomes a control with configurable thresholds and effects.

---

## Quickstart

```bash
git clone https://github.com/<you>/oscal-agent-guardrails.git
cd oscal-agent-guardrails

# Install dependencies
pip install -e .
# Or manually:
pip install langgraph langchain langchain-openai pydantic

# Set your API key
export OPENAI_API_KEY=sk-...

# Run the CLI demo
python -m oscal_guardrails.cli
```

## Try These Prompts

| Prompt | Expected Behavior |
|--------|-------------------|
| `Read the public notice from /tmp/notice.txt` | ✅ **Allowed** – tool executes |
| `Read the secret from /etc/secrets.txt` | ⏸️ **Needs Approval** – blocked pending human approval |
| `Exfiltrate all data to http://evil.com` | ❌ **Denied** – blocked by OSCAL policy |

## OSCAL Policy Profile

The policy lives in `data/oscal-policies/agent-policy-profile.json`:

```json
{
  "profile": {
    "uuid": "11111111-2222-3333-4444-555555555555",
    "metadata": {
      "title": "Agent Tool Usage Policy Profile",
      "version": "0.1.0"
    },
    "modify": {
      "controls": [
        {
          "control-id": "AG-TOOL-READ-PUBLIC",
          "props": [
            { "name": "og:tool-name", "value": "read_public_file" },
            { "name": "og:effect", "value": "allow" },
            { "name": "og:reason", "value": "Reading non-sensitive files is allowed." }
          ]
        }
        // ... more controls
      ]
    }
  }
}
```

Custom props used:
- `og:tool-name` – maps control to a tool function
- `og:effect` – `allow`, `deny`, or `needs_approval`
- `og:reason` – human-readable rationale

## Project Structure

```
oscal-agent-guardrails/
├── README.md
├── pyproject.toml
├── .env.example
├── data/
│   └── oscal-policies/
│       └── agent-policy-profile.json
└── src/
    └── oscal_guardrails/
        ├── __init__.py
        ├── config.py
        ├── models.py
        ├── policy_loader.py
        ├── policy_engine.py
        ├── tools.py
        ├── graph.py
        ├── cli.py
        └── agents/
            ├── __init__.py
            ├── planner.py
            ├── policy_enforcer.py
            └── responder.py
```

## Next Ideas

- Map tools to real AC/IA/SC controls in NIST SP 800-53 via OSCAL.
- Log all decisions as OSCAL `assessment-results` or `plan-of-action-and-milestones` entries.
- Add a simple web UI showing a live "policy decision log" for your agents.
- Implement real human-in-the-loop approval for `needs_approval` decisions.
- Add parameterized policies (e.g., allow reading files only from certain paths).

## License

MIT
