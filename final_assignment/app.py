from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from memorytown.llm_client import (
    DEFAULT_OLLAMA_MODEL,
    MockLLMClient,
    OllamaLLMClient,
    OpenAILLMClient,
    choose_default_ollama_model,
    detect_ollama_available,
    is_probably_embedding_model,
    list_ollama_models,
    normalize_ollama_host,
)
from memorytown.models import Agent, ConversationRound
from memorytown.report import generate_agent_report, save_agent_report
from memorytown.simulation import SimulationEngine
from memorytown.storage import load_sample_agents, load_state, save_state


st.set_page_config(page_title="MemoryTown AI", page_icon="🧠", layout="wide")
load_dotenv()


AI_MODES = ["샘플 모드", "OpenAI 모드", "Ollama 로컬 모드"]


def default_ai_mode() -> str:
    if os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_MODEL") or detect_ollama_available() or list_ollama_models():
        return "Ollama 로컬 모드"
    return "샘플 모드"


def build_sample_engine(llm_client=None) -> SimulationEngine:
    sample_agents = [Agent.from_sample(item) for item in load_sample_agents()]
    return SimulationEngine(agents=sample_agents, llm_client=llm_client or MockLLMClient())


def make_llm_client(mode: str, ollama_model: str | None = None):
    if mode == "OpenAI 모드":
        return OpenAILLMClient()
    if mode == "Ollama 로컬 모드":
        return OllamaLLMClient(model=ollama_model or st.session_state.get("ollama_model"))
    return MockLLMClient()


def ensure_state() -> None:
    if "ai_mode" not in st.session_state or st.session_state.ai_mode not in AI_MODES:
        st.session_state.ai_mode = default_ai_mode()
    if "ollama_host" not in st.session_state:
        st.session_state.ollama_host = normalize_ollama_host()
    if "ollama_model" not in st.session_state:
        models = list_ollama_models(st.session_state.ollama_host)
        st.session_state.ollama_model = os.getenv("OLLAMA_MODEL") or choose_default_ollama_model(models)
    if "engine" not in st.session_state:
        st.session_state.engine = build_sample_engine(make_llm_client(st.session_state.ai_mode))


def render_round(round_item: ConversationRound) -> None:
    title_bits = [f"Round {round_item.round_id}"]
    if round_item.day:
        title_bits.append(f"{round_item.day}일차")
    if round_item.time_slot:
        title_bits.append(round_item.time_slot)
    if round_item.location:
        title_bits.append(round_item.location)
    st.subheader(" / ".join(title_bits))
    st.caption(f"참여 Agent: {', '.join(round_item.participants)}")
    if round_item.topic:
        st.write(f"주제: {round_item.topic}")
    for turn in round_item.turns:
        with st.chat_message("assistant"):
            st.markdown(f"**{turn.speaker}**: {turn.message}")
    with st.expander("추출된 Fact"):
        for agent_name, facts in round_item.extracted_facts.items():
            st.markdown(f"**{agent_name}**")
            if facts:
                for fact in facts:
                    st.write(f"- {fact}")
            else:
                st.write("- 추출된 Fact가 없습니다.")
    with st.expander("업데이트된 Reflection"):
        for viewer, targets in round_item.reflections.items():
            st.markdown(f"**{viewer}의 시점**")
            for target, summary in targets.items():
                st.write(f"- {target}: {summary}")


ensure_state()
engine: SimulationEngine = st.session_state.engine

st.title("MemoryTown AI")
st.caption("캐릭터 Agent가 하루를 계획하고, 같은 장소에서 만나 대화하며, 기억과 관계를 쌓는 시뮬레이션")

with st.sidebar:
    st.header("실행 설정")
    selected_mode = st.radio("대화 엔진", AI_MODES, index=AI_MODES.index(st.session_state.ai_mode))
    if selected_mode != st.session_state.ai_mode:
        st.session_state.ai_mode = selected_mode
        engine.llm_client = make_llm_client(selected_mode)
        st.rerun()
    st.write(f"현재 모드: **{st.session_state.ai_mode}**")
    if selected_mode == "OpenAI 모드":
        if os.getenv("OPENAI_API_KEY"):
            st.success(f"OpenAI 모델: {os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')}")
        else:
            st.warning("OPENAI_API_KEY가 없어 샘플 응답으로 대체됩니다.")
    if selected_mode == "Ollama 로컬 모드":
        st.session_state.ollama_host = normalize_ollama_host()
        installed_models = list_ollama_models(st.session_state.ollama_host)
        if installed_models:
            if st.session_state.ollama_model not in installed_models:
                st.session_state.ollama_model = choose_default_ollama_model(installed_models)
            selected_model = st.selectbox(
                "설치된 Ollama 모델",
                installed_models,
                index=installed_models.index(st.session_state.ollama_model),
                help="현재 컴퓨터의 Ollama에 설치된 모델 목록입니다. 목록은 Ollama /api/tags에서 불러옵니다.",
            )
        else:
            selected_model = st.text_input(
                "Ollama 모델명",
                value=st.session_state.ollama_model,
                help="설치된 모델을 찾지 못하면 직접 모델명을 입력할 수 있습니다. 예: llama3.1:8b",
            )
        if selected_model != st.session_state.ollama_model:
            st.session_state.ollama_model = selected_model
            engine.llm_client = make_llm_client(selected_mode, ollama_model=selected_model)
            st.rerun()
        if is_probably_embedding_model(selected_model):
            st.warning("선택한 모델은 임베딩용일 가능성이 높아 대화 생성에는 적합하지 않을 수 있습니다.")
        if st.button("Ollama 모델 목록 새로고침"):
            engine.llm_client = make_llm_client(selected_mode, ollama_model=st.session_state.ollama_model)
            st.rerun()
        ollama_client = engine.llm_client if isinstance(engine.llm_client, OllamaLLMClient) else make_llm_client(selected_mode)
        st.write(f"Ollama 주소: `{ollama_client.host}`")
        st.write(f"Ollama 모델: `{ollama_client.model}`")
        if ollama_client.available_models:
            st.caption(f"인식된 로컬 모델 {len(ollama_client.available_models)}개: {', '.join(ollama_client.available_models)}")
        if ollama_client.is_ready:
            st.success("로컬 Ollama 서버를 감지했습니다.")
        else:
            st.warning("Ollama 서버를 찾지 못해 샘플 응답으로 대체됩니다.")
        for message in ollama_client.error_messages[-2:]:
            st.caption(message)

    st.divider()
    if st.button("샘플 상태로 초기화"):
        st.session_state.engine = build_sample_engine(make_llm_client(st.session_state.ai_mode))
        st.rerun()
    if st.button("현재 상태 저장"):
        path = save_state(engine)
        st.success(f"저장 완료: {path}")
    if Path("data/simulation_state.json").exists() and st.button("저장 상태 불러오기"):
        st.session_state.engine = load_state("data/simulation_state.json", llm_client=make_llm_client(st.session_state.ai_mode))
        st.rerun()

tabs = st.tabs(
    [
        "서비스 소개",
        "Agent 생성",
        "수동 대화 라운드",
        "하루 / 이틀 자동 시뮬레이션",
        "Memory 확인",
        "Relation Map 확인",
        "최종 리포트",
        "상태 점검",
    ]
)

with tabs[0]:
    st.header("서비스 소개")
    st.markdown(
        """
        **MemoryTown AI**는 여러 AI Agent가 가상의 하루 일정을 계획하고 같은 장소에서 만나 대화하는 관계 시뮬레이션 서비스입니다.

        Agent는 이름, 나이, 직업, 성격을 가지고 있으며 대화가 끝날 때마다 Fact를 Memory에 저장합니다.
        또한 상대 Agent를 어떻게 기억하고 느끼는지 Relation Map에 Reflection으로 남깁니다.

        이 구조는 게임 NPC, 교육용 역할극, 시나리오 제작, AI 캐릭터 테스트 서비스로 확장할 수 있습니다.
        """
    )
    st.info("OpenAI 또는 Ollama 모드를 연결하면 실제 모델 응답으로 대화와 요약을 생성할 수 있습니다.")

with tabs[1]:
    st.header("Agent 생성 / 수정")
    agent_names = [agent.name for agent in engine.list_agents()]
    selected = st.selectbox("수정할 Agent", ["새 Agent"] + agent_names)
    editing = selected != "새 Agent"
    current = engine.get_agent(selected) if editing else None

    with st.form("agent_form"):
        name = st.text_input("이름", value=current.name if current else "", disabled=editing)
        age = st.number_input("나이", min_value=1, max_value=120, value=current.age if current else 25)
        job = st.text_input("직업", value=current.job if current else "")
        personality = st.text_area("성격", value=current.personality if current else "")
        initial_memory = st.text_area("초기 Memory", placeholder="한 줄에 하나씩 입력합니다. 새 Agent 생성 시에 저장됩니다.")
        submitted = st.form_submit_button("저장")
        if submitted:
            if not name.strip() or not job.strip() or not personality.strip():
                st.error("이름, 직업, 성격을 모두 입력하세요.")
            elif editing and current:
                current.age = int(age)
                current.job = job.strip()
                current.personality = personality.strip()
                st.success(f"{current.name} Agent를 수정했습니다.")
            else:
                agent = Agent(name=name.strip(), age=int(age), job=job.strip(), personality=personality.strip())
                agent.add_initial_memory([line.strip() for line in initial_memory.splitlines()])
                engine.upsert_agent(agent)
                st.success(f"{agent.name} Agent를 생성했습니다.")

    st.subheader("현재 Agent 목록")
    st.table(
        [
            {"이름": agent.name, "나이": agent.age, "직업": agent.job, "성격": agent.personality}
            for agent in engine.list_agents()
        ]
    )
    if editing and st.button(f"{selected} 삭제"):
        engine.delete_agent(selected)
        st.rerun()

with tabs[2]:
    st.header("수동 대화 라운드")
    names = [agent.name for agent in engine.list_agents()]
    participants = st.multiselect("참여 Agent", names, default=names[:2])
    turns = st.slider("발언 횟수", min_value=2, max_value=12, value=4)
    topic = st.text_input("대화 주제", placeholder="비워두면 Memory 기반으로 자연스럽게 시작합니다.")
    if st.button("대화 실행", disabled=len(participants) < 2):
        try:
            result = engine.run_conversation_round(participants, turns=turns, topic=topic or None)
            render_round(result)
        except Exception as exc:
            st.error(f"대화 실행 실패: {exc}")
    if engine.rounds:
        with st.expander("최근 대화 라운드 보기"):
            render_round(engine.rounds[-1])

with tabs[3]:
    st.header("하루 / 이틀 자동 시뮬레이션")
    st.write("활동 시간은 08:00~22:00이며, 2시간 단위로 장소 계획을 세웁니다.")
    days = st.radio("시뮬레이션 기간", [1, 2], index=1, format_func=lambda value: f"{value}일")
    auto_turns = st.slider("자동 대화 발언 횟수", min_value=2, max_value=8, value=4)
    if st.button("자동 시뮬레이션 실행", disabled=len(engine.list_agents()) < 2):
        with st.spinner("Agent별 계획 생성과 장소 기반 대화를 진행 중입니다."):
            result = engine.run_automatic_simulation(days=days, turns_per_round=auto_turns)
        st.success(f"계획 {len(result['plans'])}개, 대화 라운드 {len(result['rounds'])}개를 생성했습니다.")

    st.subheader("Daily Plan")
    if engine.daily_plans:
        plan_rows = []
        for plan in engine.daily_plans:
            row = {"Agent": plan.agent_name, "일차": plan.day}
            row.update(plan.slots)
            plan_rows.append(row)
        st.table(plan_rows)
    else:
        st.write("아직 생성된 계획이 없습니다.")

    st.subheader("자동 대화 로그")
    auto_rounds = [round_item for round_item in engine.rounds if round_item.day is not None]
    for round_item in auto_rounds[-10:]:
        with st.expander(f"Round {round_item.round_id} - {round_item.day}일차 {round_item.time_slot} {round_item.location}"):
            render_round(round_item)

with tabs[4]:
    st.header("Memory 확인")
    names = [agent.name for agent in engine.list_agents()]
    if names:
        selected_agent = st.selectbox("Memory를 볼 Agent", names, key="memory_agent")
        agent = engine.get_agent(selected_agent)
        rows = [
            {
                "Round": item.round_id,
                "대상 Agent": item.subject_agent,
                "Fact": item.fact,
                "일차": item.day or "",
                "시간": item.time_slot or "",
                "출처": item.source,
            }
            for item in agent.memory
        ]
        st.table(rows if rows else [{"안내": "저장된 Memory가 없습니다."}])

with tabs[5]:
    st.header("Relation Map 확인")
    names = [agent.name for agent in engine.list_agents()]
    if names:
        selected_agent = st.selectbox("Relation Map을 볼 Agent", names, key="relation_agent")
        agent = engine.get_agent(selected_agent)
        if agent.relations:
            for target_name, relation in agent.relations.items():
                st.subheader(target_name)
                st.write(relation.summary)
                st.caption(f"업데이트 Round: {', '.join(map(str, relation.rounds))} / {relation.updated_at}")
        else:
            st.write("아직 형성된 관계 요약이 없습니다.")

with tabs[6]:
    st.header("최종 리포트")
    names = [agent.name for agent in engine.list_agents()]
    if names:
        report_agent = st.selectbox("리포트 기준 Agent", names, key="report_agent")
        markdown = generate_agent_report(engine.get_agent(report_agent), engine.list_agents())
        st.download_button(
            "Markdown 파일 다운로드",
            data=markdown,
            file_name=f"{report_agent}_final_report.md",
            mime="text/markdown",
        )
        if st.button("reports 폴더에 저장"):
            path = save_agent_report(markdown, "reports", report_agent)
            st.success(f"저장 완료: {path}")
        st.markdown(markdown)

with tabs[7]:
    st.header("상태 점검")
    checklist = [
        "Agent가 이름, 나이, 직업, 성격, Memory, Relation Map을 가진다.",
        "초기 Memory를 주입할 수 있다.",
        "2명 이상의 Agent가 turns 설정에 따라 대화한다.",
        "topic이 없으면 Memory 기반으로 대화를 시작한다.",
        "처음 만나는 Agent는 인사와 자기소개를 한다.",
        "대화 후 Fact를 추출하고 본인을 제외한 참여자 Memory에 저장한다.",
        "Agent 쌍별 Reflection을 업데이트한다.",
        "08:00~22:00 시간대와 공간 목록을 바탕으로 Daily Plan을 만든다.",
        "같은 장소에 있는 Agent끼리 자동 대화한다.",
        "특정 Agent 기준 리포트를 화면 출력 및 파일 저장할 수 있다.",
        "OPENAI_API_KEY와 OPENAI_MODEL 환경변수를 지원한다.",
        "OLLAMA_HOST와 OLLAMA_MODEL 환경변수를 지원하고 로컬 Ollama 서버를 감지한다.",
        "외부 모델 연결이 없으면 샘플 모드로 실행된다.",
    ]
    for item in checklist:
        st.checkbox(item, value=True, disabled=True)
