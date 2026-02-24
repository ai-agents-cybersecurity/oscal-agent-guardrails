from __future__ import annotations

from dataclasses import dataclass

import pytest
from langchain_core.messages import AIMessage

from oscal_guardrails import cli


@dataclass
class FakeApp:
    reply: str = "stub reply"
    fail: bool = False

    def invoke(self, _state):
        if self.fail:
            raise RuntimeError("boom")
        return {"messages": [AIMessage(content=self.reply)]}


def _set_inputs(monkeypatch: pytest.MonkeyPatch, values: list[str]) -> None:
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))


def test_cli_exits_cleanly(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "build_graph", lambda: FakeApp())
    _set_inputs(monkeypatch, ["exit"])

    cli.main()

    out = capsys.readouterr().out
    assert "OSCAL Agent Guardrails" in out


def test_cli_runs_one_prompt(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "build_graph", lambda: FakeApp(reply="allowed"))
    _set_inputs(monkeypatch, ["read public file", "exit"])

    cli.main()

    out = capsys.readouterr().out
    assert "Agent: allowed" in out


def test_cli_propagates_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "build_graph", lambda: FakeApp(fail=True))
    _set_inputs(monkeypatch, ["trigger error"])

    with pytest.raises(RuntimeError, match="boom"):
        cli.main()
