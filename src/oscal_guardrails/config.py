# src/oscal_guardrails/config.py
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

OSCAL_POLICY_PROFILE_PATH = (
    BASE_DIR / "data" / "oscal-policies" / "agent-policy-profile.json"
)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
