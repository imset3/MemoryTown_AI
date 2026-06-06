from memorytown.llm_client import MockLLMClient
from memorytown.models import Agent
from memorytown.report import generate_agent_report, save_agent_report
from memorytown.simulation import SimulationEngine


def test_final_report_contains_facts_and_reflection(tmp_path):
    agents = [
        Agent(name="민준", age=29, job="AI 서비스 기획자", personality="호기심이 많다"),
        Agent(name="서연", age=24, job="컴퓨터공학 학생", personality="차분하다"),
    ]
    engine = SimulationEngine(agents=agents, llm_client=MockLLMClient())
    engine.run_conversation_round(["민준", "서연"], turns=4, topic="MemoryTown")

    report = generate_agent_report(engine.get_agent("민준"), engine.list_agents())

    assert "MemoryTown AI 최종 리포트" in report
    assert "알고 있는 사실" in report
    assert "관계 요약 / Reflection" in report
    assert "서연" in report

    path = save_agent_report(report, tmp_path, "민준")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == report
