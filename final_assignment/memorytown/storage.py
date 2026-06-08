from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm_client import LLMClient, MockLLMClient
from .simulation import SimulationEngine


DEFAULT_STATE_PATH = Path("data/simulation_state.json")


def save_json(path: str | Path, data: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    return json.loads(target.read_text(encoding="utf-8"))


def save_state(engine: SimulationEngine, path: str | Path = DEFAULT_STATE_PATH) -> Path:
    return save_json(path, engine.to_dict())


def load_state(
    path: str | Path = DEFAULT_STATE_PATH,
    llm_client: LLMClient | None = None,
) -> SimulationEngine:
    data = load_json(path)
    return SimulationEngine.from_dict(data, llm_client=llm_client or MockLLMClient())


def load_sample_agents(path: str | Path = "data/sample_agents.json") -> list:
    data = load_json(path)
    return data.get("agents", [])
