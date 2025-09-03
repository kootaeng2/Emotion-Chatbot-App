---
title: Emotion Chatbot
emoji: 🤗
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---


# 🤖 일기 기반 감정 분석 및 콘텐츠 추천 웹
> 하루를 마무리하며 쓰는 당신의 일기, 그 속에 숨겨진 진짜 감정은 무엇일까요?
> 이 프로젝트는 AI를 통해 당신의 글을 이해하고, 감정에 몰입하거나 혹은 새로운 활력이 필요할 때 맞춤형 콘텐츠를 추천해주는 당신만의 감성 비서입니다.


<br>

<br>

## 🚀 라이브 데모 (Live Demo)
👉 https://huggingface.co/spaces/koons/emotion-chatbot
(위 주소는 실제 배포된 Space ID 기준입니다.)

<br>

# ✨ 핵심 기능
🤖 텍스트 속 감정 탐색: klue/roberta-base 모델을 한국어 '감성대화 말뭉치' 데이터로 미세조정하여, 일기 속에 담긴 복합적인 감정을 85% 이상의 정확도로 분석합니다.


🎭 감성 맞춤 큐레이션: 분석된 감정을 더 깊이 음미하고 싶을 때(수용)와 새로운 기분으로 전환하고 싶을 때(전환), 두 가지 시나리오에 맞춰 영화, 음악, 책을 추천합니다.

📔 나만의 감정 기록 보관: 작성했던 일기와 AI의 감정 분석 결과를 브라우저(localStorage)에 저장하여, 과거의 감정 흐름을 언제든지 다시 돌아볼 수 있습니다.

💻 직관적인 반응형 UI: Flask와 JavaScript로 구축된 간결하고 사용하기 쉬운 인터페이스를 제공하여, 어떤 기기에서도 편안하게 감정을 기록할 수 있습니다.

<br>

# ⚙️ 기술 스택 및 아키텍처
| 구분 | 기술 |
| :--- | :--- |
| **Backend** | python, Flask, Gunicorn |
| **Frontend**| HTML, CSS, JavaScript |
| **AI / Data**| PyTorch, Hugging Face Transformers, Scikit-learn, Pandas |
| **Deployment**| Docker, GitHub Actions, Hugging Face Spaces |
| **Version Control**| Git, GitHub, Git LFS |



<br>


Git Push (main 브랜치) → GitHub Actions (CI/CD 트리거) → Dockerfile 빌드 → Hugging Face Spaces (자동 배포 및 서빙)

<br>

## 🚀 시작하기: 로컬 환경 설정 및 실행 (Getting Started)

Python 3.10
이 프로젝트는 독립된 가상환경에서 실행하는 것을 강력하게 권장합니다. 가상환경은 PC의 다른 파이썬 프로젝트와 라이브러리가 충돌하는 것을 방지해주는 '독립된 작업 공간'입니다.

### 🌍 방법 1: Anaconda 사용 (가장 안정적인 방법)

AI/ML 프로젝트에 필요한 복잡한 라이브러리들을 가장 안정적으로 관리해주는 Anaconda 사용을 추천합니다.

```
# 1. GitHub에서 프로젝트 복제
git clone [https://github.com/kootaeng2/Emotion-Chatbot-App.git](https://github.com/kootaeng2/Emotion-Chatbot-App.git)
cd Emotion-Chatbot-App

2. 가상환경 생성 및 라이브러리 설치 (Anaconda 권장)

# Anaconda 가상환경 생성 및 활성화
conda create -n sentiment_env python=3.10
conda activate sentiment_env

# 필수 라이브러리 설치 (PyTorch 먼저, 이후 requirements.txt)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. 'sentiment_env'라는 이름으로 Python 3.10 Conda 가상환경 생성
conda create -n sentiment_env python=3.10

# 3. 새로 만든 가상환경 활성화
conda activate sentiment_env

# 4. 필수 라이브러리 설치 (PyTorch 먼저, 이후 requirements.txt)
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)

pip install -r requirements.txt


<<<<<<< HEAD
python scripts/train_model.py
4. 웹 애플리케이션 실행
Bash

python src/app.py
서버가 실행되면, 웹 브라우저 주소창에 http://127.0.0.1:5000 을 입력하여 접속하세요.

<br>

📂 프로젝트 폴더 구조
Emotion-Chatbot-App/
│
├── .github/
│   └── workflows/
│       └── sync-to-hub.yml    # GitHub Actions 자동 배포 워크플로우
│
├── korean-emotion-classifier-final/ # 추론(Inference)용 최종 AI 모델
│
├── notebooks/
│   └── 1_explore_data.py    # 데이터 탐색용 노트북
│
├── scripts/
│   └── train_model.py       # AI 모델 훈련 스크립트
│
├── src/
│   ├── app.py               # Flask 웹 서버 실행 파일
│   ├── emotion_engine.py    # 감정 분석 엔진 모듈
│   ├── recommender.py       # 콘텐츠 추천 모듈
│   ├── static/              # CSS, Frontend JS 등 정적 파일
│   └── templates/           # HTML 템플릿 파일
│
├── Dockerfile               # Hugging Face 배포용 Docker 설정
├── README.md                # 프로젝트 설명서 (현재 보고 있는 파일)
└── requirements.txt         # 필수 Python 라이브러리 목록
=======
# 📂 최종 폴더 구조
프로젝트의 가독성과 확장성을 위해 Flask 애플리케이션의 표준 구조를 따릅니다.

```Emotion-Chatbot-App/
└── src/
    ├── app.py               # Flask 웹 서버 실행 파일
    ├── emotion_engine.py    # 감정 분석 엔진 모듈
    ├── recommender.py       # 추천 로직 모듈
    ├── static/              # CSS, 클라이언트 JS 파일
    └── templates/           # HTML 템플릿 파일```

<br>

🧗‍♂️ 주요 개발 도전 과제 및 해결 과정 (Troubleshooting Journey)
이 프로젝트의 가장 큰 성과는 단순 기능 구현을 넘어, 실제 서비스 배포 과정에서 발생하는 복잡하고 깊이 있는 문제들을 체계적으로 해결한 경험입니다.

원인 불명의 OS 레벨 오류 해결 (stat: ... not NoneType):

문제: 로컬 Windows 환경에서 transformers 라이브러리가 파일을 로드하지 못하는 원인 불명의 OS 수준 오류가 지속적으로 발생.

해결: venv의 불안정성을 의심하고 Anaconda 환경으로 이전하여 환경 변수를 통제했으며, Windows와 Linux의 경로 차이를 해결하기 위해 절대 경로 사용 및 경로 구분자 정규화를 통해 문제를 최종 해결. 이를 통해 운영체제 간 호환성에 대한 깊은 이해를 얻음.

대용량 AI 모델의 버전 관리 (Git LFS & History Rewriting):

문제: 1GB가 넘는 AI 모델 및 훈련 부산물 파일로 인해 git push 시 타임아웃(408) 및 GitHub 용량 제한(GH001) 오류 발생.

해결: Git LFS를 도입하여 대용량 파일을 관리하고, 과거 히스토리에 남은 불필요한 대용량 파일의 흔적을 git filter-repo 명령어로 완전히 제거. 최종적으로 문제가 지속되자 저장소를 초기화하고 깨끗한 버전만 푸시하는 과감한 결정을 통해 근본 원인을 해결.

클라우드 자동 배포 파이프라인 구축 (CI/CD):

문제: Hugging Face Space 배포 과정에서 구식 인증 방식 오류, requirements.txt 누락, Python 모듈 탐색 경로 문제(ModuleNotFoundError), Flask 템플릿 경로 문제(TemplateNotFound) 등 다양한 런타임 오류 발생.

<<<<<<< HEAD
해결:

**Dockerfile**을 작성하여 어떤 환경에서든 동일하게 실행될 수 있는 표준화된 환경을 구축.

GitHub Actions 워크플로우를 최신 공식 Action(huggingface/sync-to-hub)으로 수정하여 인증 문제를 해결.

서버 환경에서의 Python 임포트 방식을 이해하고 **상대 경로 임포트(relative import)**를 적용하여 모듈 경로 문제를 해결.

Flask의 동작 원리에 맞춰 templates 폴더를 src 내부로 재배치하여 최종적으로 모든 런타임 오류를 해결하고 배포에 성공.
=======
해결: gunicorn의 작동 방식을 이해하고, Python의 **상대 경로 임포트(relative import)**를 적용하여 모듈 경로 문제를 해결. 또한 Flask의 기본 규칙에 맞게 templates 및 static 폴더를 app.py가 있는 src 폴더 내부로 재배치하여 문제를 최종 해결.
>>>>>>> ab2ab5ffd4245a72b03da09445175c7aec11934c
