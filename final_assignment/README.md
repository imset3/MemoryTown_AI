# MemoryTown AI

이 폴더는 교수님 확인용 최종 제출본입니다. 이 위치에서 바로 설치, 실행, 테스트할 수 있습니다.
다운로드: GitHub Releases에서 `MemoryTown_AI_project.zip`을 내려받거나, 저장소의 초록색 `Code` 버튼에서 `Download ZIP`을 선택하세요.
빠른 실행: `pip install -r requirements.txt` 후 `streamlit run app.py`로 시작합니다.

MemoryTown AI는 여러 캐릭터 Agent가 하루 일정을 계획하고, 같은 장소에서 만나 대화하며, 서로에 대한 기억과 관계를 쌓는 Streamlit 기반 시뮬레이션입니다.

Agent는 이름, 나이, 직업, 성격을 가지고 시작합니다. 대화가 끝나면 대화에서 드러난 Fact가 Memory로 저장되고, 상대를 어떻게 기억하는지 Relation Map에 Reflection이 갱신됩니다.

## 주요 기능

- Agent 생성, 수정, 삭제
- 초기 Memory 입력
- 참여 Agent와 발언 횟수를 정하는 수동 대화 라운드
- Agent별 Daily Plan 생성
- 같은 시간과 장소에 모인 Agent 간 자동 대화
- Memory와 Relation Map 확인
- 특정 Agent 시점의 Markdown 리포트 생성 및 저장
- OpenAI, Ollama, 샘플 모드 지원

## 설치

Python 3.10 이상을 권장합니다.

```bash
pip install -r requirements.txt
```

## 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시되는 로컬 주소로 접속하세요.

## 실행 모드

### 샘플 모드

외부 모델 연결 없이 전체 흐름을 확인할 수 있는 기본 모드입니다. 대화, Fact 추출, Reflection, Daily Plan이 결정적인 샘플 응답으로 동작합니다.

### Ollama 로컬 모드

Ollama가 설치되어 있고 로컬 서버가 실행 중이면 앱이 모델 목록을 읽어 사이드바에 표시합니다.

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

### OpenAI 모드

OpenAI API 키와 모델명을 환경변수 또는 `.env` 파일에 설정합니다.

```bash
cp .env.example .env
```

`.env` 예시:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4.1-mini
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

## 화면 구성

- 서비스 소개: 프로젝트 개요와 활용 방식
- Agent 생성: 샘플 Agent 확인, Agent 추가와 수정
- 수동 대화 라운드: 참여자와 발언 횟수를 정해 대화 실행
- 하루 / 이틀 자동 시뮬레이션: Daily Plan 생성 후 장소 기반 자동 대화
- Memory 확인: Agent가 알고 있는 Fact 목록 확인
- Relation Map 확인: Agent별 상대방 Reflection 확인
- 최종 리포트: 특정 Agent 시점의 Markdown 리포트 생성
- 상태 점검: 핵심 기능 구현 상태 확인

## 프로젝트 구조

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
│   ├── MemoryTown_AI_발표자료_구성.md
│   └── MemoryTown_AI_학습자료.html
├── tests/
│   ├── test_simulation.py
│   └── test_report.py
├── scripts/
│   ├── make_submission_zip.py
│   └── smoke_ollama.py
├── requirements.txt
├── README.md
└── .env.example
```

## 테스트

```bash
pytest
```

테스트는 샘플 모드를 사용하므로 API 키가 없어도 실행됩니다.

Ollama 서버가 실행 중이고 모델이 설치되어 있다면 실제 로컬 모델 smoke test도 실행할 수 있습니다.

```bash
python scripts/smoke_ollama.py
```

## 패키지 생성

배포용 zip이 필요하면 아래 명령을 사용합니다.

```bash
python scripts/make_submission_zip.py
```

생성 결과:

```text
submission/MemoryTown_AI_submission.zip
```

`.env`, `.git`, `.venv`, `__pycache__`, 개인 리포트 파일은 zip에서 제외됩니다.
