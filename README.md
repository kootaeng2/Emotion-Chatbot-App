---
title: Emotion Chatbot
emoji: 🤗
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---
🤖 일기 기반 감정 분석 및 콘텐츠 추천 웹
하루를 마무리하며 쓰는 당신의 일기, 그 속에 숨겨진 진짜 감정은 무엇일까요?
이 프로젝트는 AI를 통해 당신의 글을 이해하고, 감정에 몰입하거나 혹은 새로운 활력이 필요할 때 맞춤형 콘텐츠를 추천해주는 당신만의 감성 비서입니다.

<br>

<br>

🚀 라이브 데모 (Live Demo)
👉 https://huggingface.co/spaces/koons/emotion-chatbot
(위 주소는 이전에 확인된 Space ID 기준이며, 실제 최종 배포된 주소로 수정해주세요.)

<br>

[여기에 웹 애플리케이션 실제 작동 스크린샷이나 GIF를 삽입하세요]

<br>

✨ 핵심 기능
🤖 텍스트 속 감정 탐색: klue/roberta-base 모델을 한국어 '감성대화 말뭉치' 데이터로 미세조정하여, 일기 속에 담긴 복합적인 감정을 85% 이상의 정확도로 분석합니다.

🎭 감성 맞춤 큐레이션: 분석된 감정을 더 깊이 음미하고 싶을 때(수용)와 새로운 기분으로 전환하고 싶을 때(전환), 두 가지 시나리오에 맞춰 영화, 음악, 책을 추천합니다.

📔 나만의 감정 기록 보관: 작성했던 일기와 AI의 감정 분석 결과를 브라우저(localStorage)에 저장하여, 과거의 감정 흐름을 언제든지 다시 돌아볼 수 있습니다.

💻 직관적인 반응형 UI: Flask와 JavaScript로 구축된 간결하고 사용하기 쉬운 인터페이스를 제공하여, 어떤 기기에서도 편안하게 감정을 기록할 수 있습니다.

<br>

⚙️ 기술 스택 및 아키텍처
구분	기술
Backend	Python 3.10, Flask, Gunicorn
Frontend	HTML, CSS, JavaScript
AI / Data	PyTorch, Hugging Face Transformers, Scikit-learn, Pandas
Deployment	Docker, GitHub Actions, Hugging Face Spaces
Version Control	Git, GitHub, Git LFS

Sheets로 내보내기
<br>

배포 아키텍처 (CI/CD Pipeline)
이 프로젝트는 GitHub Actions를 이용한 자동화된 배포 파이프라인을 구축했습니다.
Git Push (main 브랜치) → GitHub Actions (CI/CD 트리거) → Dockerfile 빌드 → Hugging Face Spaces (자동 배포 및 서빙)

<br>

🛠️ 시작하기: 로컬 환경에서 실행
사전 요구사항
Python 3.10

Git

1. 프로젝트 복제 (Clone)
Bash

git clone https://github.com/kootaeng2/Emotion-Chatbot-App.git
cd Emotion-Chatbot-App
(저장소 이름이 변경되었다면, 위 주소를 새로 만드신 주소로 수정해주세요.)

2. 가상환경 생성 및 라이브러리 설치
Bash

# Python 3.10 가상환경 생성 및 활성화
py -3.10 -m venv venv
.\venv\Scripts\Activate

# PyTorch 및 기타 라이브러리 설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
3. AI 모델 직접 훈련하기 (최초 1회 필수)
⚠️ 주의: 이 프로젝트는 훈련된 모델 파일을 포함하고 있지 않습니다. AI Hub '감성대화 말뭉치' 데이터셋을 다운로드하여 data/ 폴더에 위치시킨 후, 아래 명령어를 실행해야 합니다.

Bash

python scripts/train_model.py
4. 웹 애플리케이션 실행
Bash

python src/app.py
서버가 실행되면, 웹 브라우저 주소창에 http://127.0.0.1:5000 을 입력하여 접속하세요.

<br>

📂 최종 폴더 구조
프로젝트의 가독성과 확장성을 위해 Flask 애플리케이션의 표준 구조를 따릅니다.

Emotion-Chatbot-App/
└── src/
    ├── app.py               # Flask 웹 서버 실행 파일
    ├── emotion_engine.py    # 감정 분석 엔진 모듈
    ├── recommender.py       # 추천 로직 모듈
    ├── static/              # CSS, 클라이언트 JS 파일
    └── templates/           # HTML 템플릿 파일
... (기타 프로젝트 파일 및 폴더) ...
<br>

🧗‍♂️ 주요 개발 도전 과제 및 해결 과정
이 프로젝트는 단순 기능 구현을 넘어, 실제 서비스 배포 과정에서 발생하는 복잡한 문제들을 체계적으로 해결한 경험을 포함합니다.

Git LFS 및 히스토리 문제 해결:

문제: 1GB가 넘는 AI 모델 파일로 인해 git push 시 타임아웃 및 용량 제한 오류 발생.

해결: Git LFS를 도입하고, 과거 히스토리에 남은 대용량 파일의 흔적을 git filter-repo 명령어로 완전히 제거하여 저장소를 배포에 최적화. 문제가 해결되지 않자 저장소를 초기화하는 과감한 결정을 통해 근본 원인을 해결.

Hugging Face 배포 자동화 (CI/CD):

문제: 수동 배포의 비효율성을 개선하고, GitHub와 배포 서버 간의 인증 및 동기화 오류 발생.

해결: Dockerfile로 실행 환경을 표준화하고, GitHub Actions 워크플로우를 구축하여 main 브랜치에 push 할 때마다 자동으로 Hugging Face Spaces에 배포되도록 CI/CD 파이프라인을 완성.

Flask 애플리케이션 구조 문제:

문제: 로컬에서는 정상 작동하던 앱이, Docker 및 Gunicorn 환경의 서버에 배포되자 ModuleNotFoundError, TemplateNotFound 등 경로 관련 런타임 오류 발생.

해결: gunicorn의 작동 방식을 이해하고, Python의 **상대 경로 임포트(relative import)**를 적용하여 모듈 경로 문제를 해결. 또한 Flask의 기본 규칙에 맞게 templates 및 static 폴더를 app.py가 있는 src 폴더 내부로 재배치하여 문제를 최종 해결.