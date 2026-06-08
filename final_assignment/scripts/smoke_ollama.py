from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memorytown.llm_client import OllamaLLMClient, choose_default_ollama_model, list_ollama_models
from memorytown.models import Agent
from memorytown.report import generate_agent_report, save_agent_report
from memorytown.simulation import SimulationEngine
from memorytown.storage import load_state, save_state


def main() -> None:
    os.environ.setdefault("OLLAMA_NUM_PREDICT", "160")
    models = list_ollama_models(timeout=2.0)
    if not models:
        raise RuntimeError("설치된 Ollama 모델을 찾지 못했습니다.")

    model = choose_default_ollama_model(models)
    print(f"[OK] Ollama 모델 인식: {', '.join(models)}", flush=True)
    print(f"[OK] smoke 기본 모델: {model}", flush=True)

    client = OllamaLLMClient(model=model)
    if not client.is_ready:
        raise RuntimeError(f"Ollama 서버 호출 준비 실패: {client.error_messages}")

    agents = [
        Agent(
            name="민준",
            age=29,
            job="AI 서비스 기획자",
            personality="호기심이 많고 사람들의 니즈를 잘 관찰한다",
        ),
        Agent(
            name="서연",
            age=24,
            job="컴퓨터공학 학생",
            personality="차분하고 분석적이며 새로운 기술을 빠르게 실험한다",
        ),
    ]
    agents[0].add_initial_memory(["민준은 MemoryTown AI를 스타트업 서비스로 발전시키고 싶어 한다."])
    agents[1].add_initial_memory(["서연은 로컬 LLM과 Agent Memory 구조에 관심이 많다."])

    engine = SimulationEngine(
        agents=agents,
        llm_client=client,
        time_slots=["08:00"],
        locations=["카페"],
    )

    before_errors = len(client.error_messages)
    manual = engine.run_conversation_round(["민준", "서연"], turns=2, topic=None)
    assert len(manual.turns) == 2
    assert engine.get_agent("민준").known_facts_about("서연")
    assert engine.get_agent("서연").known_facts_about("민준")
    assert engine.get_agent("민준").relations["서연"].summary
    print("[OK] 수동 대화, topic 없음, 첫 만남 자기소개, Fact 저장, Reflection 업데이트", flush=True)

    topic_round = engine.run_conversation_round(["민준", "서연"], turns=2, topic="관계 맵 화면 설계")
    assert topic_round.topic == "관계 맵 화면 설계"
    print("[OK] topic 있는 수동 대화", flush=True)

    auto = engine.run_automatic_simulation(days=1, turns_per_round=2)
    assert auto["plans"]
    assert auto["rounds"]
    assert all(round_item.location == "카페" for round_item in auto["rounds"])
    print(f"[OK] 자동 계획 및 같은 장소 자동 대화: 계획 {len(auto['plans'])}개, 라운드 {len(auto['rounds'])}개", flush=True)

    report = generate_agent_report(engine.get_agent("민준"), engine.list_agents())
    assert "서연" in report and "관계 요약 / Reflection" in report
    report_path = save_agent_report(report, Path("reports") / "smoke", "민준")
    assert report_path.exists()
    print(f"[OK] 최종 리포트 생성/저장: {report_path}", flush=True)

    state_path = Path("data") / "smoke_simulation_state.json"
    save_state(engine, state_path)
    restored = load_state(state_path, llm_client=client)
    assert restored.round_counter == engine.round_counter
    assert restored.get_agent("민준").relations
    print(f"[OK] 상태 저장/불러오기: {state_path}", flush=True)

    if len(client.error_messages) > before_errors:
        raise RuntimeError(f"Ollama 호출 중 fallback/error 발생: {client.error_messages[before_errors:]}")

    print("[DONE] Ollama 실제 모델 smoke test 통과", flush=True)


if __name__ == "__main__":
    main()
