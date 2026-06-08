# MemoryTown AI 기획서

## 프로젝트명

MemoryTown AI

## 서비스 한 줄 소개

여러 AI Agent가 하루 일정을 계획하고 같은 장소에서 만나 대화하며, 서로에 대한 기억과 관계를 형성하는 AI Agent 관계 시뮬레이션 서비스.

## 문제 정의

게임 NPC, 교육용 역할극, 시나리오 제작 도구에서 캐릭터는 대화를 해도 이전 대화와 관계 변화를 오래 유지하지 못하는 경우가 많다. 사용자는 캐릭터가 자신과 타인을 기억하고, 만남이 누적되며 관계가 변화하는 자연스러운 상호작용을 원한다.

## 목표 사용자

- 게임 NPC와 캐릭터 상호작용을 실험하려는 인디 게임 개발자
- 역할극 기반 교육 콘텐츠를 만드는 교사와 교육 스타트업
- 캐릭터 대화와 관계 변화를 테스트하려는 시나리오 작가
- LLM Agent의 Memory와 Reflection 구조를 학습하려는 학생

## 핵심 기능

- Agent 생성: 이름, 나이, 직업, 성격, 초기 Memory 입력
- 수동 대화 라운드: 참여 Agent, 발언 횟수, 선택 주제 설정
- Fact 추출: 대화 후 Agent별 사실을 LLM이 추출
- Memory 저장: 추출된 Fact를 본인을 제외한 참여자의 Memory에 저장
- Relation Map: Agent가 상대를 어떻게 기억하고 느끼는지 Reflection 업데이트
- Daily Plan: 하루 시작 전 Agent별 시간대 장소 계획 생성
- 자동 시뮬레이션: 같은 시간, 같은 장소의 Agent끼리 자동 대화
- 최종 리포트: 특정 Agent 시점에서 상대방별 Fact와 Reflection 출력 및 저장

## AI 활용 방식

MemoryTown AI는 LLM을 네 가지 지점에서 활용한다.

1. 대화 생성: Agent의 성격, 직업, Memory, Relation Map을 반영해 한국어 대화를 만든다.
2. Fact 추출: 대화 로그에서 Agent별로 기억할 만한 사실을 JSON 형태로 추출한다.
3. Reflection 업데이트: 대화와 누적 Memory를 바탕으로 상대 Agent에 대한 관계 요약을 갱신한다.
4. Daily Planning: 각 Agent가 하루 동안 어느 장소에 있을지 시간대별 계획을 세운다.

API Key가 없는 개발 환경에서는 샘플 모드가 같은 인터페이스로 동작한다. Ollama가 설치된 환경에서는 `OLLAMA_HOST`, `OLLAMA_MODEL`을 통해 로컬 LLM으로도 실행할 수 있다. 앱은 Ollama `/api/tags`에서 현재 컴퓨터에 설치된 모델 목록을 인식하고, 사용자가 사이드바에서 원하는 로컬 모델을 선택할 수 있게 한다.

## 데이터 구조

- Agent: name, age, job, personality, memory, relations
- MemoryItem: round_id, subject_agent, fact, day, time_slot, source, created_at
- RelationReflection: target_agent, summary, rounds, updated_at
- ConversationTurn: speaker, message
- ConversationRound: round_id, participants, topic, day, time_slot, location, turns, extracted_facts, reflections
- DailyPlan: agent_name, day, slots

## 구현 플랫폼

- Python
- Streamlit
- OpenAI API 또는 Ollama 로컬 LLM
- python-dotenv
- pytest

## 서비스 화면 구성

1. 서비스 소개: 프로젝트 개요와 AI 활용 방식 안내
2. Agent 생성: 샘플 Agent 확인, Agent 추가와 수정
3. 수동 대화 라운드: 참여자와 발언 횟수를 정해 즉시 대화 실행
4. 하루 / 이틀 자동 시뮬레이션: Daily Plan 생성 후 장소 기반 자동 대화
5. Memory 확인: Agent가 알고 있는 Fact 목록 확인
6. Relation Map 확인: Agent별 상대방 Reflection 확인
7. 최종 리포트: 특정 Agent 시점의 Markdown 리포트 생성
8. 상태 점검: 핵심 기능 동작 상태 확인

## 스타트업 확장 가능성

- 게임 개발사를 위한 NPC 관계 시뮬레이션 API
- 교육 기관용 역할극 학습 시나리오 제작 도구
- 웹소설, 드라마, 게임 시나리오 작가를 위한 캐릭터 관계 테스트 도구
- AI 캐릭터 서비스의 장기 기억 평가 및 디버깅 플랫폼

## 수익 모델 아이디어

- 개인 창작자를 위한 월 구독형 SaaS
- 게임 스튜디오 대상 프로젝트 단위 라이선스
- 교육 기관용 좌석 기반 요금제
- Agent Memory 분석 리포트와 시나리오 템플릿 유료 판매
- 고급 LLM 모델, 장기 시뮬레이션, 관계 그래프 시각화 기능을 포함한 Pro 플랜

## 기대 효과

- 캐릭터 관계 변화와 장기 기억 구조를 쉽게 실험할 수 있다.
- LLM Agent가 단발성 대화가 아니라 누적된 맥락을 기반으로 상호작용한다.
- 시나리오 제작자는 여러 캐릭터의 관계 변화를 빠르게 검토할 수 있다.
- 학생은 Agent, Memory, Reflection, Planning Prompt 구조를 실습할 수 있다.

## 한계점과 개선 방향

- 현재 Relation Map은 텍스트 요약 중심이므로 그래프 시각화가 추가되면 이해가 쉬워진다.
- 샘플 모드는 흐름 확인에는 충분하지만 실제 응답 품질 검증에는 OpenAI 모드 또는 Ollama 로컬 모드가 필요하다.
- Agent 수가 많아질수록 대화 라운드와 LLM 호출 비용이 증가한다.
- 향후 벡터 DB를 연결하면 장기 Memory 검색 품질을 높일 수 있다.
- 향후 사용자 편집 가능한 장소, 시간표, 성격 프리셋을 추가할 수 있다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

OpenAI 모드는 `.env` 파일 또는 환경변수에 `OPENAI_API_KEY`를 설정한 뒤 앱 사이드바에서 선택한다.
