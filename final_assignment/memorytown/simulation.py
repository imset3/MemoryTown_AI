from __future__ import annotations

from itertools import combinations
from typing import Any

from .llm_client import LLMClient, MockLLMClient
from .models import Agent, ConversationRound, DailyPlan, MemoryItem, RelationReflection, now_iso


DEFAULT_TIME_SLOTS = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
DEFAULT_LOCATIONS = ["집", "학교", "카페", "레스토랑", "도서관", "회사"]


class SimulationEngine:
    def __init__(
        self,
        agents: list[Agent] | None = None,
        llm_client: LLMClient | None = None,
        time_slots: list[str] | None = None,
        locations: list[str] | None = None,
    ) -> None:
        self.agents: dict[str, Agent] = {agent.name: agent for agent in agents or []}
        self.llm_client = llm_client or MockLLMClient()
        self.time_slots = time_slots or DEFAULT_TIME_SLOTS.copy()
        self.locations = locations or DEFAULT_LOCATIONS.copy()
        self.rounds: list[ConversationRound] = []
        self.daily_plans: list[DailyPlan] = []
        self.round_counter = 0

    def list_agents(self) -> list[Agent]:
        return list(self.agents.values())

    def get_agent(self, name: str) -> Agent:
        if name not in self.agents:
            raise KeyError(f"Agent를 찾을 수 없습니다: {name}")
        return self.agents[name]

    def upsert_agent(self, agent: Agent) -> None:
        self.agents[agent.name] = agent

    def delete_agent(self, name: str) -> None:
        self.agents.pop(name, None)
        for agent in self.agents.values():
            agent.relations.pop(name, None)

    def run_conversation_round(
        self,
        participant_names: list[str],
        turns: int,
        topic: str | None = None,
        day: int | None = None,
        time_slot: str | None = None,
        location: str | None = None,
    ) -> ConversationRound:
        if len(participant_names) < 2:
            raise ValueError("대화에는 Agent가 2명 이상 필요합니다.")
        participants = [self.get_agent(name) for name in participant_names]
        self.round_counter += 1
        first_meeting = self._is_first_meeting(participants)
        conversation_turns = self.llm_client.generate_conversation(
            participants,
            turns=max(1, turns),
            topic=topic.strip() if topic else None,
            round_id=self.round_counter,
            first_meeting=first_meeting,
        )
        extracted_facts = self.llm_client.extract_facts(participants, conversation_turns)
        self._store_facts(participants, extracted_facts, self.round_counter, day, time_slot)
        reflections = self._update_reflections(participants, conversation_turns, self.round_counter)
        round_result = ConversationRound(
            round_id=self.round_counter,
            participants=participant_names,
            topic=topic.strip() if topic else None,
            day=day,
            time_slot=time_slot,
            location=location,
            turns=conversation_turns,
            extracted_facts=extracted_facts,
            reflections=reflections,
        )
        self.rounds.append(round_result)
        return round_result

    def create_daily_plans(self, day: int) -> list[DailyPlan]:
        plans = [
            self.llm_client.create_daily_plan(agent, day, self.time_slots, self.locations)
            for agent in self.list_agents()
        ]
        self.daily_plans = [plan for plan in self.daily_plans if plan.day != day]
        self.daily_plans.extend(plans)
        return plans

    def run_automatic_simulation(self, days: int = 2, turns_per_round: int = 4) -> dict[str, Any]:
        created_rounds: list[ConversationRound] = []
        created_plans: list[DailyPlan] = []
        for day in range(1, days + 1):
            day_plans = self.create_daily_plans(day)
            created_plans.extend(day_plans)
            for time_slot in self.time_slots:
                by_location: dict[str, list[str]] = {}
                for plan in day_plans:
                    by_location.setdefault(plan.slots[time_slot], []).append(plan.agent_name)
                for location, names in by_location.items():
                    if len(names) >= 2:
                        round_result = self.run_conversation_round(
                            participant_names=names,
                            turns=turns_per_round,
                            topic=f"{day}일차 {time_slot} {location}에서의 자연스러운 만남",
                            day=day,
                            time_slot=time_slot,
                            location=location,
                        )
                        created_rounds.append(round_result)
        return {"plans": created_plans, "rounds": created_rounds}

    def _is_first_meeting(self, participants: list[Agent]) -> bool:
        for left, right in combinations(participants, 2):
            if right.name not in left.relations or left.name not in right.relations:
                return True
        return False

    def _store_facts(
        self,
        participants: list[Agent],
        extracted_facts: dict[str, list[str]],
        round_id: int,
        day: int | None,
        time_slot: str | None,
    ) -> None:
        participant_names = {agent.name for agent in participants}
        for subject_name, facts in extracted_facts.items():
            if subject_name not in participant_names:
                continue
            for listener in participants:
                if listener.name == subject_name:
                    continue
                for fact in facts:
                    listener.add_memory(
                        MemoryItem(
                            round_id=round_id,
                            subject_agent=subject_name,
                            fact=fact,
                            day=day,
                            time_slot=time_slot,
                        )
                    )

    def _update_reflections(
        self,
        participants: list[Agent],
        turns: list,
        round_id: int,
    ) -> dict[str, dict[str, str]]:
        reflections: dict[str, dict[str, str]] = {}
        for viewer in participants:
            reflections[viewer.name] = {}
            for target in participants:
                if viewer.name == target.name:
                    continue
                known_facts = [item.fact for item in viewer.known_facts_about(target.name)]
                previous = viewer.relations.get(target.name)
                summary = self.llm_client.update_reflection(
                    viewer=viewer,
                    target=target,
                    turns=turns,
                    known_facts=known_facts,
                    previous_reflection=previous.summary if previous else None,
                )
                old_rounds = previous.rounds if previous else []
                viewer.relations[target.name] = RelationReflection(
                    target_agent=target.name,
                    summary=summary,
                    rounds=[*old_rounds, round_id],
                    updated_at=now_iso(),
                )
                reflections[viewer.name][target.name] = summary
        return reflections

    def to_dict(self) -> dict[str, Any]:
        return {
            "agents": [agent.to_dict() for agent in self.list_agents()],
            "rounds": [round_item.to_dict() for round_item in self.rounds],
            "daily_plans": [plan.__dict__ for plan in self.daily_plans],
            "round_counter": self.round_counter,
            "time_slots": self.time_slots,
            "locations": self.locations,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], llm_client: LLMClient | None = None) -> "SimulationEngine":
        from .models import ConversationRound

        engine = cls(
            agents=[Agent.from_dict(item) for item in data.get("agents", [])],
            llm_client=llm_client or MockLLMClient(),
            time_slots=data.get("time_slots") or DEFAULT_TIME_SLOTS.copy(),
            locations=data.get("locations") or DEFAULT_LOCATIONS.copy(),
        )
        engine.rounds = [ConversationRound.from_dict(item) for item in data.get("rounds", [])]
        engine.daily_plans = [DailyPlan.from_dict(item) for item in data.get("daily_plans", [])]
        engine.round_counter = int(data.get("round_counter", len(engine.rounds)))
        return engine
