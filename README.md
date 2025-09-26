---
title: Emotion Chatbot
emoji: 🤗
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
# persistent_storage: 1G 
pinned: false
---


# 🤖 일기 기반 감정 분석 및 콘텐츠 추천 웹
> 하루를 마무리하며 쓰는 당신의 일기, 그 속에 숨겨진 진짜 감정은 무엇일까요?
> 이 프로젝트는 AI를 통해 당신의 글을 이해하고, 감정에 몰입하거나 혹은 새로운 활력이 필요할 때 맞춤형 콘텐츠를 추천해주는 당신만의 감성 비서입니다.


<br>

<br>

## 🚀 라이브 데모 (Live Demo)
👉 https://huggingface.co/spaces/taehoon222/emotion-chatbot-app


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
| **Backend** | python, Flask, Gunicorn, SQAlchemy |
| **Frontend**| HTML, CSS, JavaScript |
| **AI / Data**| PyTorch, Hugging Face Transformers, Scikit-learn, Pandas |
| **Datebase**| Supabase(postgreSQL)
| **Deployment**| Docker, GitHub Actions(CI/CD), Hugging Face Spaces |
| **Version Control**| Git, GitHub, Git LFS |



<br>

# 🏛️ 아키텍처 및 배포 파이프라인
가벼운 앱 코드와 무거운 AI 모델을 분리하여 효율적인 CI/CD 파이프라인을 구축했습니다.

[로컬 PC] git push → [GitHub] (main 브랜치) → [GitHub Actions 트리거] → [Hugging Face Spaces로 코드 배포] → [Spaces 서버 실행] → (실행 시) [Hugging Face Hub에서 모델 다운로드]


<br>

## 🚀 시작하기: 로컬 환경 설정 및 실행 (Getting Started)

Python 3.10
이 프로젝트는 독립된 가상환경에서 실행하는 것을 강력하게 권장합니다. 가상환경은 PC의 다른 파이썬 프로젝트와 라이브러리가 충돌하는 것을 방지해주는 '독립된 작업 공간'입니다.

### 🌍 방법 1: Anaconda 사용 (가장 안정적인 방법)

AI/ML 프로젝트에 필요한 복잡한 라이브러리들을 가장 안정적으로 관리해주는 Anaconda 사용을 추천합니다.

```
# 1. GitHub에서 프로젝트 복제
git clone https://github.com/kootaeng2/Emotion-Chatbot-App.git
cd Emotion-Chatbot-App

2. 가상환경 생성 및 라이브러리 설치 (Anaconda 권장)

# Anaconda 가상환경 생성 및 활성화
conda create -n sentiment_env python=3.10
conda activate sentiment_env

# 필수 라이브러리 설치 (PyTorch 먼저, 이후 requirements.txt)
pip install -r requirements.txt

# 3. 새로 만든 가상환경 활성화
conda activate sentiment_env

4. 웹 애플리케이션 실행
python src/app.py

서버가 실행되면, 웹 브라우저 주소창에 http://127.0.0.1:5000 을 입력하여 접속하세요.

```
<br>

# 📂 프로젝트 폴더 구조
```
Emotion-Chatbot-App/
│
├── .github/
│   └── workflows/
│       └── sync-to-hub.yml      # GitHub Actions 자동 배포 워크플로우
│
├── notebooks/
│   └── 1_explore_data.py        # 데이터 탐색용 노트북
│
├── scripts/
│   └── train_model.py           # AI 모델 훈련 스크립트
│   └── test.py                  # Huggingface 연결 확인
│   └── upload_model.py          # huggingface 업로드 확인
│
│
├── src/
│   └── templastes               # 홈페이지 html정리
│       └── emotion_homepage.py  # 메인 화면
│       └── login.py             # 로그인 화면
│       └── signup.py            # 회원가입 화면
│
│   ├── __init__.py              # Flask Application Factory, 앱 생성 및 설정
│   ├── main.py                  # 메인페이지, API 등 핵심 라우트
│   ├── auth.py                  # 로그인, 회원가입 등 인증 라우트
│   ├── models.py                # SQLAlchemy DB 모델 (User, Diary)
│   ├── emotion_engine.py        # 감정 분석 엔진 (모델 로딩 및 추론)
│   └── recommender.py           # 콘텐츠 추천 로직
│
├── run.py                       # 애플리케이션 실행 스크립트
├── .gitattributes               # Git 이용시 주의사항
├── .gitignore                   # Git 추적 제외 목록
├── Dockerfile                   # Hugging Face 배포용 Docker 설정
├── README.md                    # 프로젝트 설명서 (현재 보고 있는 파일)
└── requirements.txt             # 필수 Python 라이브러리 목록
```

<br>

🧗‍♂️ 주요 개발 도전 과제 및 해결 과정 (Troubleshooting Journey)
이 프로젝트의 가장 큰 성과는 단순 기능 구현을 넘어, 실제 서비스 배포 과정에서 발생하는 복잡하고 깊이 있는 문제들을 체계적으로 해결한 경험입니다.

1. 대용량 AI 모델 관리 및 배포 전략 수립
🔍 문제: 1GB가 넘는 AI 모델 파일을 Git LFS로 관리했으나, Hugging Face Spaces의 1GB 저장 공간 한계(Storage limit reached)와 LFS 파일-포인터 불일치(LFS pointer does not exist) 등 배포 과정에서 지속적인 오류 발생.

💡 해결: 모델과 앱 코드의 완전한 분리 전략을 채택.

대용량 모델은 Hugging Face Hub에 별도로 업로드하여 버전 관리.

GitHub 저장소에서는 LFS 추적을 완전히 제거하고 순수 앱 코드만 관리.

**GitHub Actions 워크플로우(lfs: false)**를 수정하여 배포 시에는 앱 코드만 Spaces로 푸시하도록 변경.

Spaces 앱 실행 시점에서 emotion_engine.py가 Hub로부터 모델을 다운로드하도록 하여, 저장 공간 문제를 근본적으로 해결하고 효율적인 배포 파이프라인을 완성.

2. CI/CD 파이프라인의 분산 환경 인증 문제 해결
🔍 문제: git push로 트리거된 GitHub Actions가 Hugging Face Spaces에 접근할 때 Invalid credentials 인증 오류 발생. Spaces의 Secret과 GitHub의 Secret 역할에 대한 혼동.

💡 해결: **'배포 로봇(GitHub Actions)'**과 **'빌드 로봇(Spaces)'**의 개념으로 역할을 명확히 분리.

GitHub Actions Secret (HF_TOKEN): '배포 로봇'이 Hugging Face에 코드를 푸시할 때 필요한 write 권한 토큰을 등록.

Hugging Face Spaces Secret (HF_TOKEN): '빌드 로봇'이 내부적으로 LFS 파일 등을 처리할 때 필요한 write 권한 토큰을 등록.

이를 통해 각기 다른 환경에서 필요한 인증을 명확히 분리하여 CI/CD 파이프라인의 인증 문제를 해결.

3. Flask 애플리케이션 구조 설계 및 런타임 오류 디버깅
🔍 문제: 개발 초기, 단일 파일 구조로 인해 모듈 경로 탐색 오류(ModuleNotFoundError)가 발생하고, AI 모델을 매번 API 호출 시마다 로딩하여 극심한 성능 저하.

💡 해결: Flask의 Application Factory 패턴을 도입하여 프로젝트 구조를 체계적으로 재설계.

__init__.py에서 create_app 함수를 통해 앱의 모든 구성요소(DB, 블루프린트, 설정)를 조립.

앱 시작 시점에서 AI 모델을 단 한 번만 로드하여 app 객체에 저장(app.emotion_classifier).

각 API 요청에서는 current_app을 통해 미리 로드된 모델을 참조하게 하여, 메모리 효율성과 응답 속도를 극대화. 이를 통해 확장 가능하고 안정적인 백엔드 구조를 완성.


