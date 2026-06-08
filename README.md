# MemoryTown AI

교수님께: 이 저장소는 weekly assignment와 final assignment를 분리해 정리했습니다.

- Weekly 정리: [`weekly_assignment/`](./weekly_assignment/)
- Final 최종 제출본: [`final_assignment/`](./final_assignment/)
- 전체 zip 다운로드: [GitHub Release](https://github.com/imset3/MemoryTown_AI/releases/tag/v1.0.0)에서 `MemoryTown_AI_project.zip`을 받으면 됩니다.

## 한 줄 요약

MemoryTown AI는 여러 AI Agent가 하루 일정을 계획하고, 같은 장소에서 만나 대화하며, 서로에 대한 Memory와 Relation Map을 쌓는 Streamlit 기반 AI 관계 시뮬레이션입니다.

## 교수님이 바로 보시면 좋은 순서

1. [`final_assignment/README.md`](./final_assignment/README.md): 실행 방법과 프로젝트 요약
2. [`final_assignment/app.py`](./final_assignment/app.py): Streamlit 구현물
3. [`final_assignment/docs/MemoryTown_AI_기획서.md`](./final_assignment/docs/MemoryTown_AI_기획서.md): 제출용 기획서
4. [`final_assignment/docs/MemoryTown_AI_발표자료_구성.md`](./final_assignment/docs/MemoryTown_AI_발표자료_구성.md): 발표자료 구성
5. [`final_assignment/docs/MemoryTown_AI_학습자료.html`](./final_assignment/docs/MemoryTown_AI_학습자료.html): 비전공자용 학습자료

## 실행 방법

```bash
cd final_assignment
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시되는 로컬 주소로 접속하면 됩니다.

## AI 실행 모드

- Mock 모드: API 키 없이 전체 흐름을 확인하는 샘플 모드
- Ollama 로컬 모드: 현재 컴퓨터에 설치된 Ollama 모델을 자동 인식해 실행
- Real AI 모드: `.env` 또는 환경변수의 `OPENAI_API_KEY`, `OPENAI_MODEL` 사용

Ollama 서버가 실행 중이고 모델이 설치되어 있다면 실제 로컬 모델 smoke test도 가능합니다.

```bash
cd final_assignment
python scripts/smoke_ollama.py
```

## 과제 조건 충족 요약

| 조건 | 충족 위치 |
| --- | --- |
| AI 스타트업 서비스 기획 | `final_assignment/docs/MemoryTown_AI_기획서.md` |
| Streamlit 구현물 | `final_assignment/app.py` |
| AI 기능 실제 작동 | OpenAI / Ollama / Mock LLM 클라이언트 |
| Agent, Memory, Relation Map | `final_assignment/memorytown/models.py` |
| 대화, Fact 추출, Reflection | `final_assignment/memorytown/simulation.py` |
| 자동 Daily Plan 및 장소 기반 대화 | `final_assignment/memorytown/simulation.py` |
| 최종 리포트 | `final_assignment/memorytown/report.py` |
| 테스트 | `final_assignment/tests/` |

## 저장소 구조

```text
.
├── weekly_assignment/      # weekly assignment 정리
├── final_assignment/       # 교수님 확인용 최종 제출본
├── README.md               # 저장소 전체 안내
└── pytest.ini              # 루트 테스트 탐색 범위 설정
```

## 다운로드 방법

GitHub에서 바로 확인하려면 `final_assignment/` 폴더를 열면 됩니다.

압축 파일로 받으려면 아래 Release에서 `MemoryTown_AI_project.zip`을 다운로드하세요.

```text
https://github.com/imset3/MemoryTown_AI/releases/tag/v1.0.0
```

## 검증 상태

- 루트 테스트 통과
- `final_assignment/` 내부 테스트 통과
- Ollama 실제 모델 smoke test 통과
- Release zip에 `.env` 미포함 확인
