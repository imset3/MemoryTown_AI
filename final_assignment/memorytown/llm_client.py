from __future__ import annotations

import json
import os
import random
import subprocess
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .models import Agent, ConversationTurn, DailyPlan


DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
DEFAULT_OLLAMA_NUM_PREDICT = 512
EMBEDDING_MODEL_HINTS = ("embed", "embedding", "bge", "nomic-embed")


class LLMClient(ABC):
    """Interface used by the simulation engine."""

    @abstractmethod
    def generate_conversation(
        self,
        agents: list[Agent],
        turns: int,
        topic: str | None,
        round_id: int,
        first_meeting: bool = False,
    ) -> list[ConversationTurn]:
        raise NotImplementedError

    @abstractmethod
    def extract_facts(self, agents: list[Agent], turns: list[ConversationTurn]) -> dict[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def update_reflection(
        self,
        viewer: Agent,
        target: Agent,
        turns: list[ConversationTurn],
        known_facts: list[str],
        previous_reflection: str | None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_daily_plan(
        self,
        agent: Agent,
        day: int,
        time_slots: list[str],
        locations: list[str],
    ) -> DailyPlan:
        raise NotImplementedError


def parse_json_object(raw: str, fallback: dict[str, Any]) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1).replace("JSON\n", "", 1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return fallback
    return fallback


def normalize_ollama_host(host: str | None = None) -> str:
    return (host or os.getenv("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST).rstrip("/")


def detect_ollama_available(host: str | None = None, timeout: float = 0.4) -> bool:
    target = f"{normalize_ollama_host(host)}/api/tags"
    try:
        with urllib.request.urlopen(target, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (OSError, urllib.error.URLError):
        return False


def list_ollama_models_from_manifests(models_dir: str | Path | None = None) -> list[str]:
    root = Path(models_dir or os.getenv("OLLAMA_MODELS") or Path.home() / ".ollama" / "models")
    manifests = root / "manifests"
    if not manifests.exists():
        return []

    models: set[str] = set()
    for path in manifests.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(manifests)
        parts = relative.parts
        if len(parts) < 4:
            continue
        namespace_parts = list(parts[1:-2])
        model_name = parts[-2]
        tag = parts[-1]
        if namespace_parts == ["library"]:
            models.add(f"{model_name}:{tag}")
        else:
            namespace = "/".join(namespace_parts)
            models.add(f"{namespace}/{model_name}:{tag}")
    return sorted(models)


def list_ollama_models_from_cli(timeout: float = 2.0) -> list[str]:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []

    models: list[str] = []
    for index, line in enumerate(result.stdout.splitlines()):
        if index == 0 or not line.strip():
            continue
        name = line.split()[0]
        if name and name != "NAME":
            models.append(name)
    return sorted(set(models))


def list_ollama_models(host: str | None = None, timeout: float = 1.5) -> list[str]:
    target = f"{normalize_ollama_host(host)}/api/tags"
    models: list[str] = []
    try:
        with urllib.request.urlopen(target, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            models = [item.get("name", "") for item in data.get("models", [])]
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        models = []
    merged = set(model for model in models if model)
    merged.update(list_ollama_models_from_manifests())
    merged.update(list_ollama_models_from_cli())
    return sorted(merged)


def is_probably_embedding_model(model: str) -> bool:
    lowered = model.lower()
    return any(hint in lowered for hint in EMBEDDING_MODEL_HINTS)


def choose_default_ollama_model(models: list[str]) -> str:
    for model in models:
        if not is_probably_embedding_model(model):
            return model
    return models[0] if models else DEFAULT_OLLAMA_MODEL


class MockLLMClient(LLMClient):
    """Deterministic local client used when no model connection is available."""

    def generate_conversation(
        self,
        agents: list[Agent],
        turns: int,
        topic: str | None,
        round_id: int,
        first_meeting: bool = False,
    ) -> list[ConversationTurn]:
        if len(agents) < 2:
            raise ValueError("대화에는 Agent가 2명 이상 필요합니다.")

        messages: list[ConversationTurn] = []
        total_turns = max(1, turns)
        subject = topic.strip() if topic else None
        for index in range(total_turns):
            speaker = agents[index % len(agents)]
            others = [agent.name for agent in agents if agent.name != speaker.name]
            if first_meeting and index < len(agents):
                text = (
                    f"안녕하세요, 저는 {speaker.name}입니다. "
                    f"{speaker.job}이고, 제 성격은 {speaker.personality}에 가까워요."
                )
            elif subject:
                text = (
                    f"{speaker.name}은(는) '{subject}'에 대해 이야기하며 "
                    f"{speaker.job} 관점에서 {', '.join(others)}와 생각을 나눕니다."
                )
            else:
                memory_hint = speaker.memory[-1].fact if speaker.memory else "오늘 새롭게 알게 된 일"
                text = (
                    f"{speaker.name}은(는) 기억 속 '{memory_hint}'을(를) 떠올리며 "
                    f"{', '.join(others)}에게 자연스럽게 질문합니다."
                )
            messages.append(ConversationTurn(speaker=speaker.name, message=text))
        return messages

    def extract_facts(self, agents: list[Agent], turns: list[ConversationTurn]) -> dict[str, list[str]]:
        result = {agent.name: [] for agent in agents}
        agent_names = set(result)
        for turn in turns:
            if turn.speaker in agent_names:
                sentence = turn.message.strip()
                if sentence:
                    result[turn.speaker].append(f"{turn.speaker}은(는) 대화에서 '{sentence[:80]}'라고 말했다.")
        return result

    def update_reflection(
        self,
        viewer: Agent,
        target: Agent,
        turns: list[ConversationTurn],
        known_facts: list[str],
        previous_reflection: str | None,
    ) -> str:
        target_lines = [turn.message for turn in turns if turn.speaker == target.name]
        if not target_lines:
            return previous_reflection or f"{viewer.name}은(는) {target.name}을(를) 아직 잘 알지 못한다."
        latest = target_lines[-1][:70]
        fact_count = len(known_facts)
        return (
            f"{viewer.name}은(는) {target.name}을(를) {target.personality}한 {target.job}로 기억한다. "
            f"최근 발언 '{latest}'을(를) 통해 관심사를 조금 더 이해했고, 알고 있는 사실은 {fact_count}개다."
        )

    def create_daily_plan(
        self,
        agent: Agent,
        day: int,
        time_slots: list[str],
        locations: list[str],
    ) -> DailyPlan:
        rng = random.Random(f"{agent.name}-{day}")
        slots: dict[str, str] = {}
        job_location = self._job_location(agent.job, locations)
        for index, time_slot in enumerate(time_slots):
            if time_slot in {"10:00", "14:00"} and job_location:
                location = job_location
            elif time_slot == "12:00" and "레스토랑" in locations:
                location = "레스토랑"
            elif time_slot == "16:00" and "카페" in locations:
                location = "카페"
            elif time_slot == "20:00" and "집" in locations:
                location = "집"
            else:
                location = locations[(rng.randrange(len(locations)) + index + day) % len(locations)]
            slots[time_slot] = location
        return DailyPlan(agent_name=agent.name, day=day, slots=slots)

    @staticmethod
    def _job_location(job: str, locations: list[str]) -> str | None:
        if "학생" in job and "학교" in locations:
            return "학교"
        if "개발" in job or "기획" in job or "회사" in job:
            return "회사" if "회사" in locations else None
        if "작가" in job and "도서관" in locations:
            return "도서관"
        if "디자이너" in job and "카페" in locations:
            return "카페"
        return None


class OpenAILLMClient(LLMClient):
    """OpenAI-backed client with deterministic local fallbacks."""

    def __init__(self, model: str | None = None) -> None:
        load_dotenv()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.error_messages: list[str] = []
        self._mock = MockLLMClient()
        self._client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=api_key)
            except Exception as exc:  # pragma: no cover - depends on local package state
                self.error_messages.append(f"OpenAI 클라이언트 초기화 실패: {exc}")
        else:
            self.error_messages.append("OPENAI_API_KEY가 없어 샘플 응답으로 대체합니다.")

    @property
    def is_ready(self) -> bool:
        return self._client is not None

    def _json_chat(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self._client:
            return fallback
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
            return parse_json_object(content, fallback)
        except Exception as exc:  # pragma: no cover - requires real API
            self.error_messages.append(f"OpenAI 호출 실패: {exc}")
            return fallback

    def generate_conversation(
        self,
        agents: list[Agent],
        turns: int,
        topic: str | None,
        round_id: int,
        first_meeting: bool = False,
    ) -> list[ConversationTurn]:
        fallback_turns = self._mock.generate_conversation(agents, turns, topic, round_id, first_meeting)
        fallback = {"turns": [turn.__dict__ for turn in fallback_turns]}
        agent_payload = [
            {
                "name": agent.name,
                "age": agent.age,
                "job": agent.job,
                "personality": agent.personality,
                "recent_memory": [item.fact for item in agent.memory[-5:]],
                "relations": {name: rel.summary for name, rel in agent.relations.items()},
            }
            for agent in agents
        ]
        data = self._json_chat(
            "너는 한국어로 자연스러운 Agent 대화를 만드는 시뮬레이션 엔진이다. 반드시 JSON만 반환한다.",
            json.dumps(
                {
                    "task": "conversation",
                    "round_id": round_id,
                    "agents": agent_payload,
                    "turn_count": turns,
                    "topic": topic,
                    "first_meeting": first_meeting,
                    "rules": [
                        "turns 배열만 반환한다.",
                        "각 item은 speaker와 message를 가진다.",
                        "처음 만나는 경우 인사와 자기소개를 먼저 한다.",
                        "topic이 없으면 기억을 기반으로 자연스럽게 이야기한다.",
                    ],
                },
                ensure_ascii=False,
            ),
            fallback,
        )
        parsed = [
            ConversationTurn(speaker=item.get("speaker", ""), message=item.get("message", ""))
            for item in data.get("turns", [])
            if item.get("speaker") and item.get("message")
        ]
        return parsed or fallback_turns

    def extract_facts(self, agents: list[Agent], turns: list[ConversationTurn]) -> dict[str, list[str]]:
        fallback = self._mock.extract_facts(agents, turns)
        data = self._json_chat(
            "너는 대화에서 Agent별 사실을 추출하는 분석기다. 반드시 JSON만 반환한다.",
            json.dumps(
                {
                    "task": "extract_facts",
                    "agents": [agent.name for agent in agents],
                    "conversation": [turn.__dict__ for turn in turns],
                    "rules": [
                        "facts 객체를 반환한다.",
                        "facts의 key는 Agent 이름, value는 그 Agent에 대한 한국어 사실 문자열 배열이다.",
                        "추측보다 대화에서 드러난 사실 위주로 쓴다.",
                    ],
                },
                ensure_ascii=False,
            ),
            {"facts": fallback},
        )
        facts = data.get("facts", fallback)
        return {agent.name: list(facts.get(agent.name, [])) for agent in agents}

    def update_reflection(
        self,
        viewer: Agent,
        target: Agent,
        turns: list[ConversationTurn],
        known_facts: list[str],
        previous_reflection: str | None,
    ) -> str:
        fallback = self._mock.update_reflection(viewer, target, turns, known_facts, previous_reflection)
        data = self._json_chat(
            "너는 Agent가 상대를 어떻게 기억하고 느끼는지 한국어로 요약하는 관계 Reflection 작성기다. 반드시 JSON만 반환한다.",
            json.dumps(
                {
                    "task": "update_reflection",
                    "viewer": viewer.name,
                    "target": {
                        "name": target.name,
                        "age": target.age,
                        "job": target.job,
                        "personality": target.personality,
                    },
                    "previous_reflection": previous_reflection,
                    "known_facts": known_facts[-10:],
                    "conversation": [turn.__dict__ for turn in turns],
                    "format": {"reflection": "한 문단 한국어 요약"},
                },
                ensure_ascii=False,
            ),
            {"reflection": fallback},
        )
        return data.get("reflection") or fallback

    def create_daily_plan(
        self,
        agent: Agent,
        day: int,
        time_slots: list[str],
        locations: list[str],
    ) -> DailyPlan:
        fallback_plan = self._mock.create_daily_plan(agent, day, time_slots, locations)
        data = self._json_chat(
            "너는 Agent의 하루 장소 계획을 만드는 Planning Prompt 엔진이다. 반드시 JSON만 반환한다.",
            json.dumps(
                {
                    "task": "create_daily_plan",
                    "agent": {
                        "name": agent.name,
                        "age": agent.age,
                        "job": agent.job,
                        "personality": agent.personality,
                        "memory": [item.fact for item in agent.memory[-8:]],
                    },
                    "day": day,
                    "time_slots": time_slots,
                    "locations": locations,
                    "rules": [
                        "slots 객체의 key는 time_slots의 값만 사용한다.",
                        "slots 객체의 value는 locations 중 하나만 사용한다.",
                    ],
                },
                ensure_ascii=False,
            ),
            {"slots": fallback_plan.slots},
        )
        slots = {
            slot: data.get("slots", {}).get(slot, fallback_plan.slots[slot])
            for slot in time_slots
            if data.get("slots", {}).get(slot, fallback_plan.slots[slot]) in locations
        }
        if len(slots) != len(time_slots):
            slots = fallback_plan.slots
        return DailyPlan(agent_name=agent.name, day=day, slots=slots)


class OllamaLLMClient(OpenAILLMClient):
    """Ollama local LLM client using the same JSON prompt contract as OpenAI."""

    def __init__(self, model: str | None = None, host: str | None = None) -> None:
        load_dotenv()
        self.host = normalize_ollama_host(host)
        self.available_models = list_ollama_models(self.host)
        env_model = os.getenv("OLLAMA_MODEL")
        self.model = model or env_model or choose_default_ollama_model(self.available_models)
        self.error_messages: list[str] = []
        self._mock = MockLLMClient()
        self._available = self._probe()

    @property
    def is_ready(self) -> bool:
        return self._available

    def _probe(self) -> bool:
        if not detect_ollama_available(self.host, timeout=0.6):
            self.error_messages.append(
                f"Ollama 서버를 찾지 못해 샘플 응답으로 대체합니다. 확인 주소: {self.host}"
            )
            return False
        try:
            self.available_models = list_ollama_models(self.host)
            if self.available_models and self.model not in self.available_models:
                self.error_messages.append(
                    f"Ollama 서버는 감지됐지만 '{self.model}' 모델이 목록에 없습니다. "
                    f"설치된 모델: {', '.join(self.available_models)}"
                )
            return True
        except Exception as exc:
            self.error_messages.append(f"Ollama 상태 확인 실패: {exc}")
            return False

    def _request_json(
        self,
        path: str,
        payload: dict[str, Any],
        method: str = "POST",
        timeout: float = 90.0,
    ) -> dict[str, Any]:
        data = None if method == "GET" else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _json_chat(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self._available:
            return fallback
        try:
            num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", str(DEFAULT_OLLAMA_NUM_PREDICT)))
            data = self._request_json(
                "/api/chat",
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": num_predict},
                },
            )
            content = data.get("message", {}).get("content", "")
            return parse_json_object(content, fallback)
        except Exception as exc:
            self.error_messages.append(f"Ollama 호출 실패: {exc}")
            return fallback
