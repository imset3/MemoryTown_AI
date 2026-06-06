from memorytown.llm_client import MockLLMClient, OllamaLLMClient
from memorytown.models import Agent
from memorytown.simulation import SimulationEngine
from memorytown.storage import load_state, save_state


def make_engine() -> SimulationEngine:
    agents = [
        Agent(name="민준", age=29, job="AI 서비스 기획자", personality="호기심이 많다"),
        Agent(name="서연", age=24, job="컴퓨터공학 학생", personality="차분하고 분석적이다"),
    ]
    agents[0].add_initial_memory(["민준은 카페에서 아이디어를 정리한다."])
    agents[1].add_initial_memory(["서연은 도서관에서 프로젝트를 한다."])
    return SimulationEngine(agents=agents, llm_client=MockLLMClient())


def test_agent_creation_with_initial_memory():
    agent = Agent(name="하린", age=27, job="UX 디자이너", personality="공감 능력이 높다")
    agent.add_initial_memory(["하린은 관계 맵 화면을 구상한다."])

    assert agent.name == "하린"
    assert agent.memory[0].source == "initial"
    assert "관계 맵" in agent.memory[0].fact


def test_conversation_round_saves_memory_and_reflection():
    engine = make_engine()
    result = engine.run_conversation_round(["민준", "서연"], turns=4, topic=None)

    minjun = engine.get_agent("민준")
    seoyeon = engine.get_agent("서연")

    assert result.round_id == 1
    assert len(result.turns) == 4
    assert seoyeon.known_facts_about("민준")
    assert minjun.known_facts_about("서연")
    assert "서연" in minjun.relations
    assert "민준" in seoyeon.relations


def test_automatic_simulation_creates_plans_and_rounds():
    engine = make_engine()
    result = engine.run_automatic_simulation(days=2, turns_per_round=2)

    assert len(result["plans"]) == 4
    assert len(engine.daily_plans) == 4
    assert len(result["rounds"]) >= 1
    assert all(round_item.day in {1, 2} for round_item in result["rounds"])


def test_save_and_load_state(tmp_path):
    engine = make_engine()
    engine.run_conversation_round(["민준", "서연"], turns=2, topic="프로젝트 아이디어")
    path = tmp_path / "simulation_state.json"

    save_state(engine, path)
    restored = load_state(path, llm_client=MockLLMClient())

    assert restored.round_counter == 1
    assert restored.get_agent("민준").relations["서연"].summary


def test_ollama_client_falls_back_when_server_is_unavailable():
    client = OllamaLLMClient(host="http://127.0.0.1:9", model="missing-test-model")
    agents = [
        Agent(name="민준", age=29, job="AI 서비스 기획자", personality="호기심이 많다"),
        Agent(name="서연", age=24, job="컴퓨터공학 학생", personality="차분하다"),
    ]

    turns = client.generate_conversation(agents, turns=2, topic="로컬 테스트", round_id=1)

    assert not client.is_ready
    assert len(turns) == 2
    assert client.error_messages
