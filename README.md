# MemoryTown AI
요약: AI Agent가 하루를 계획하고 만나 대화하며 Memory와 Relation Map을 쌓는 Streamlit 기반 관계 시뮬레이션 과제입니다.
다운로드: GitHub Releases에서 `MemoryTown_AI_project.zip`을 내려받거나, 저장소의 초록색 `Code` 버튼에서 `Download ZIP`을 선택하세요.
빠른 실행: 압축 해제 후 `pip install -r requirements.txt`를 실행하고 `streamlit run app.py`로 시작합니다.

MemoryTown AI는 여러 AI Agent가 가상의 하루 일정을 계획하고, 같은 장소에서 만나 대화하며, 서로에 대한 기억과 관계를 형성하는 Streamlit 기반 AI Agent 관계 시뮬레이션 서비스입니다.

게임 NPC, 교육용 역할극, 시나리오 제작, AI 캐릭터 테스트 서비스로 확장 가능한 스타트업 아이템을 목표로 합니다.

## 과제 요구사항 매핑표

| 과제 요구사항 | 구현 내용 |
| --- | --- |
| AI 스타트업 서비스 기획 및 구현 | 기획서, 발표자료 구성, Streamlit 앱 제공 |
| 구현 플랫폼 Streamlit | `app.py` |
| AI 기능 1개 이상 실제 작동 | OpenAI 또는 Ollama 기반 대화 생성, Fact 추출, Reflection, Daily Plan |
| API Key 하드코딩 금지 | `.env` 또는 `OPENAI_API_KEY` 환경변수 사용 |
| Mock 모드 | API Key나 로컬 LLM 없이도 `MockLLMClient`로 전체 기능 실행 |
| Agent 기본 구조 | `memorytown/models.py` |
| Memory와 Relation Map | 대화 후 Fact 저장 및 Reflection 업데이트 |
| 2명 이상 대화 | 수동 대화 라운드에서 참여 Agent 선택 |
| 선택 topic | topic 미입력 시 Memory 기반 대화 |
| 처음 만남 인사 | 첫 관계가 없는 Agent는 인사와 자기소개부터 시작 |
| 가상 일정과 장소 | 08:00~22:00, 2시간 단위, 6개 장소 |
| 같은 장소 자동 대화 | 자동 시뮬레이션 탭 |
| 특정 Agent 리포트 | 최종 리포트 탭에서 Markdown 다운로드 및 저장 |
| 테스트 | `tests/` |
| 제출 zip | `scripts/make_submission_zip.py` |

## 설치 방법

Python 3.10 이상을 권장합니다.

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시되는 로컬 주소로 접속합니다.

## GitHub Release 다운로드 방법

1. 저장소 오른쪽의 `Releases`를 클릭합니다.
2. 최신 릴리즈에서 `MemoryTown_AI_project.zip`을 다운로드합니다.
3. 압축을 풀고 프로젝트 폴더에서 `pip install -r requirements.txt`를 실행합니다.
4. `streamlit run app.py`로 앱을 실행합니다.

## Mock 모드 실행 방법

API Key가 없어도 기본 실행됩니다.

1. `streamlit run app.py` 실행
2. 사이드바에서 `Mock 모드` 선택
3. 수동 대화 또는 자동 시뮬레이션 실행

Mock 모드는 개발과 제출 화면 확인을 위한 대체 모드입니다. **제출 전 실제 AI 모드로 실행 필요**합니다.

## Ollama 로컬 모드 실행 방법

Ollama가 설치되어 있고 로컬 서버가 실행 중이면 앱이 환경을 감지해 `Ollama 로컬 모드`를 사용할 수 있습니다. `OLLAMA_HOST` 또는 `OLLAMA_MODEL` 환경변수가 있거나 `http://localhost:11434` 서버가 응답하면 로컬 AI 모드 후보로 인식합니다.

앱은 현재 컴퓨터의 Ollama `/api/tags`를 읽어 설치된 로컬 모델 목록을 자동으로 불러옵니다. 사이드바의 `설치된 Ollama 모델` 선택 상자에서 원하는 모델을 고르면 이후 대화, Fact 추출, Reflection, Daily Plan 생성에 해당 모델을 사용합니다.

예시:

```bash
ollama pull llama3.1:8b
ollama serve
```

다른 터미널에서 실행합니다.

```bash
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.1:8b
streamlit run app.py
```

`.env` 파일에도 설정할 수 있습니다.

```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

Ollama 서버나 모델 호출이 실패하면 앱이 중단되지 않고 Mock 응답으로 대체됩니다.

## Real AI 모드 실행 방법

OpenAI API Key를 설정한 뒤 앱 사이드바에서 `Real AI 모드`를 선택합니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값을 입력합니다.

```bash
OPENAI_API_KEY=실제_API_KEY
OPENAI_MODEL=gpt-4.1-mini
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

환경변수로 직접 실행해도 됩니다.

```bash
export OPENAI_API_KEY=실제_API_KEY
export OPENAI_MODEL=gpt-4.1-mini
streamlit run app.py
```

`OPENAI_MODEL` 값을 바꾸면 사용할 모델명을 변경할 수 있습니다.

## 화면별 사용 방법

- 서비스 소개: 서비스 개요와 확장 가능성을 확인합니다.
- Agent 생성: 샘플 Agent를 확인하고 새 Agent를 추가하거나 기존 Agent를 수정합니다.
- 수동 대화 라운드: 참여 Agent, 발언 횟수, 선택 주제를 설정하고 대화를 실행합니다.
- 하루 / 이틀 자동 시뮬레이션: Agent별 Daily Plan을 만들고 같은 장소의 Agent끼리 자동 대화시킵니다.
- Memory 확인: 특정 Agent가 알고 있는 Fact를 확인합니다.
- Relation Map 확인: 특정 Agent가 상대를 어떻게 기억하고 느끼는지 확인합니다.
- 최종 리포트: 특정 Agent 기준 Markdown 리포트를 생성하고 다운로드하거나 `reports/` 폴더에 저장합니다.
- 제출 체크리스트: 과제 요구사항 충족 여부를 확인합니다.

## 제출 전 체크리스트

- `streamlit run app.py`가 정상 실행되는지 확인
- Mock 모드에서 수동 대화와 자동 시뮬레이션이 작동하는지 확인
- Ollama를 사용할 경우 `ollama serve`와 `ollama pull 모델명`을 확인
- `.env`에 실제 `OPENAI_API_KEY`를 설정한 뒤 Real AI 모드가 작동하는지 확인
- 최종 리포트가 Markdown으로 다운로드되는지 확인
- `pytest`가 통과하는지 확인
- 제출 zip을 생성하고 포함 파일을 확인

## 폴더 구조

```text
.
├── app.py
├── memorytown/
│   ├── __init__.py
│   ├── models.py
│   ├── llm_client.py
│   ├── simulation.py
│   ├── report.py
│   └── storage.py
├── data/
│   └── sample_agents.json
├── docs/
│   ├── MemoryTown_AI_기획서.md
│   └── MemoryTown_AI_발표자료_구성.md
├── tests/
│   ├── test_simulation.py
│   └── test_report.py
├── scripts/
│   └── make_submission_zip.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## 테스트 실행 방법

```bash
pytest
```

테스트는 MockLLM을 사용하므로 API Key가 없어도 실행됩니다.

## 제출용 zip 생성 방법

```bash
python scripts/make_submission_zip.py
```

생성 결과:

```text
submission/MemoryTown_AI_submission.zip
```

zip에는 `app.py`, `memorytown/`, `data/sample_agents.json`, `docs/`, `tests/`, `scripts/make_submission_zip.py`, `README.md`, `requirements.txt`, `.env.example`이 포함됩니다. `.env`, `.git`, `.venv`, `__pycache__`, 개인 리포트 파일은 제외됩니다.
