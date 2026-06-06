from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class MemoryItem:
    round_id: int
    subject_agent: str
    fact: str
    day: int | None = None
    time_slot: str | None = None
    source: str = "conversation"
    created_at: str = field(default_factory=now_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        return cls(**data)


@dataclass
class RelationReflection:
    target_agent: str
    summary: str
    rounds: list[int] = field(default_factory=list)
    updated_at: str = field(default_factory=now_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationReflection":
        return cls(**data)


@dataclass
class ConversationTurn:
    speaker: str
    message: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationTurn":
        return cls(**data)


@dataclass
class ConversationRound:
    round_id: int
    participants: list[str]
    turns: list[ConversationTurn]
    topic: str | None = None
    day: int | None = None
    time_slot: str | None = None
    location: str | None = None
    extracted_facts: dict[str, list[str]] = field(default_factory=dict)
    reflections: dict[str, dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationRound":
        copied = dict(data)
        copied["turns"] = [ConversationTurn.from_dict(item) for item in copied.get("turns", [])]
        return cls(**copied)


@dataclass
class DailyPlan:
    agent_name: str
    day: int
    slots: dict[str, str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DailyPlan":
        return cls(**data)


@dataclass
class Agent:
    name: str
    age: int
    job: str
    personality: str
    memory: list[MemoryItem] = field(default_factory=list)
    relations: dict[str, RelationReflection] = field(default_factory=dict)

    def add_initial_memory(self, facts: list[str]) -> None:
        for fact in facts:
            cleaned = fact.strip()
            if cleaned:
                self.memory.append(
                    MemoryItem(
                        round_id=0,
                        subject_agent=self.name,
                        fact=cleaned,
                        source="initial",
                    )
                )

    def add_memory(self, item: MemoryItem) -> None:
        if item.fact.strip():
            self.memory.append(item)

    def known_facts_about(self, subject_agent: str) -> list[MemoryItem]:
        return [item for item in self.memory if item.subject_agent == subject_agent]

    def relation_summary_for(self, target_agent: str) -> str:
        relation = self.relations.get(target_agent)
        return relation.summary if relation else "아직 형성된 관계 요약이 없습니다."

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "age": self.age,
            "job": self.job,
            "personality": self.personality,
            "memory": [asdict(item) for item in self.memory],
            "relations": {key: asdict(value) for key, value in self.relations.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        copied = dict(data)
        copied["memory"] = [MemoryItem.from_dict(item) for item in copied.get("memory", [])]
        copied["relations"] = {
            key: RelationReflection.from_dict(value)
            for key, value in copied.get("relations", {}).items()
        }
        return cls(**copied)

    @classmethod
    def from_sample(cls, data: dict[str, Any]) -> "Agent":
        agent = cls(
            name=data["name"],
            age=int(data["age"]),
            job=data["job"],
            personality=data["personality"],
        )
        initial_memory = data.get("initial_memory", [])
        if isinstance(initial_memory, str):
            initial_memory = [line.strip() for line in initial_memory.splitlines()]
        agent.add_initial_memory(initial_memory)
        return agent
