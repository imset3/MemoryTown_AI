# MemoryTown AI 발표자료 구성

## 1. 표지

- MemoryTown AI
- AI Agent 관계 시뮬레이션 서비스
- AI를 활용한 스타트업 서비스 기획 및 구현

## 2. 문제 정의

- 기존 캐릭터 대화는 이전 만남과 관계 변화를 잘 유지하지 못함
- 게임 NPC, 교육 역할극, 시나리오 제작에서 장기 기억형 Agent 수요 존재
- 캐릭터가 서로를 기억하고 관계를 발전시키는 구조가 필요

## 3. 서비스 아이디어

- 여러 Agent가 가상의 하루를 살아가는 시뮬레이션
- 같은 장소에 있으면 자동으로 대화 발생
- 대화 후 Fact, Memory, Reflection이 누적됨

## 4. 목표 사용자와 활용 사례

- 게임 개발자: NPC 관계 실험
- 교육자: 역할극 기반 학습 콘텐츠
- 작가: 캐릭터 관계와 대화 테스트
- 학생: LLM Agent 구조 학습

## 5. 핵심 기능

- Agent 생성: 이름, 나이, 직업, 성격, 초기 Memory
- 수동 대화 라운드
- Daily Plan 기반 자동 시뮬레이션
- Memory와 Relation Map 확인
- 최종 리포트 저장

## 6. AI 활용 구조

- Conversation Generation: Agent별 대화 생성
- Fact Extraction: 대화에서 기억할 사실 추출
- Reflection Update: 상대에 대한 관계 요약 갱신
- Planning Prompt: 시간대별 장소 계획 생성
- OpenAI API 또는 Ollama 로컬 LLM 선택 가능

## 7. 데이터 구조

- Agent
- MemoryItem
- RelationReflection
- ConversationRound
- DailyPlan
- JSON 저장과 불러오기 지원

## 8. 구현 화면

- 서비스 소개
- Agent 생성
- 수동 대화 라운드
- 하루 / 이틀 자동 시뮬레이션
- Memory 확인
- Relation Map 확인
- 최종 리포트
- 제출 체크리스트

## 9. 스타트업 확장 가능성

- NPC 관계 엔진 API
- 교육용 역할극 SaaS
- 작가용 캐릭터 시뮬레이션 도구
- 장기 기억형 AI 캐릭터 테스트 플랫폼

## 10. 한계와 개선 방향

- 현재는 텍스트 중심 Relation Map
- 향후 그래프 시각화와 벡터 DB Memory 검색 추가 가능
- Agent 수 증가 시 비용 최적화 필요
- 실제 서비스에서는 안전성 필터와 사용자별 저장소 필요
