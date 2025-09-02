---
title: Emotion Chatbot
emoji: 🤗
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---
# 🤖 일기 기반 감정 분석 및 콘텐츠 추천 웹 애플리케이션

> 사용자의 일기 텍스트를 AI로 분석하여 감정을 파악하고, '감정 수용' 또는 '기분 전환'이라는 두 가지 선택지에 따라 맞춤형 콘텐츠(영화, 음악, 책)를 추천해주는 웹 기반 서비스입니다.

<br>

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Transformers-yellow?style=for-the-badge)

<br>

## ✨ 주요 기능 (Key Features)

* **AI 기반 감정 분석:** Hugging Face의 `klue/roberta-base` 모델을 AI Hub의 '감성대화 말뭉치' 데이터셋으로 미세 조정(Fine-tuning)하여, 한국어 텍스트에 대한 높은 정확도의 감정 예측을 수행합니다.
* **상황별 맞춤 추천:** 분석된 감정에 대해 '감정을 깊이 느끼고 싶을 때(수용)'와 '감정에서 벗어나고 싶을 때(전환)'라는 두 가지 선택지를 제공하여, 사용자의 현재 니즈에 맞는 차별화된 콘텐츠를 추천합니다.
* **다이어리 히스토리:** 사용자가 작성한 일기와 AI의 분석 결과를 웹 브라우저의 `localStorage`에 저장하여, 언제든 과거의 기록을 다시 확인하고 감정의 흐름을 파악할 수 있습니다.
* **사용자 친화적 웹 인터페이스:** Flask 기반의 웹 서버와 동적인 JavaScript를 통해, 누구나 쉽게 자신의 감정을 기록하고 추천을 받을 수 있는 직관적인 UI/UX를 제공합니다.

<br>

## 🖥️ 프로젝트 데모 (Demo)

임시 홈페이지(https://kootaeng2.github.io/Emotion_Chatbot_project/templates/emotion_homepage.html)

<br>

## ⚙️ 기술 스택 (Tech Stack)

| 구분 | 기술 |
| :--- | :--- |
| **Backend** | Flask |
| **Frontend**| HTML, CSS, JavaScript |
| **AI / Data**| Python 3.10, PyTorch, Hugging Face Transformers, Scikit-learn, Pandas |
| **AI Model**| `klue/roberta-base` (Fine-tuned) |

<br>

## 📂 폴더 구조 (Folder Structure)

```
sentiment_analysis_project/
├── src/                 
│   ├── app.py           # 웹 서버 실행 파일
│   ├── chatbot.py       # 터미널 챗봇 실행 파일
│   ├── emotion_engine.py  # 감정 분석 엔진 모듈
│   └── recommender.py     # 추천 로직 모듈
├── scripts/             
│   └── train_model.py     # AI 모델 훈련 스크립트
├── notebooks/           
│   └── 1_explore_data.py  # 데이터 탐색 및 시각화용 노트북
├── data/                  # 원본 데이터셋
├── results/               # 훈련된 모델 파일 (Git 미포함)
├── templates/             # HTML 파일
├── static/                # CSS, 클라이언트 JS 파일
├── .gitignore             # Git 무시 파일 목록
├── README.md              # 프로젝트 설명서
└── requirements.txt       # 필수 라이브러리 목록
```
<br>

## 🚀 설치 및 실행 방법 (Installation & Run)

**1. 프로젝트 복제 (Clone)**
```bash
git clone [https://github.com/kootaeng2/Emotion_Chatbot_project.git](https://github.com/kootaeng2/Emotion_Chatbot_project.git)
cd Emotion_Chatbot_project
```

**2. 가상환경 생성 및 활성화 (Python 3.10 기준)**
```bash
# Python 3.10 버전을 지정하여 가상환경 생성
py -3.10 -m venv venv
# 가상환경 활성화
.\venv\Scripts\Activate
```

**3. 필수 라이브러리 설치**
```bash
# PyTorch (CUDA 11.8 버전)를 먼저 설치합니다.
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)
# 나머지 라이브러리를 설치합니다.
pip install -r requirements.txt
```

**4. AI 모델 훈련 (최초 1회 필수)**
> **주의:** 이 과정은 AI Hub에서 '감성대화 말뭉치' 원본 데이터셋을 다운로드하여 `data` 폴더에 위치시킨 후 진행해야 합니다. 훈련에는 RTX 4060 GPU 기준 약 30-40분이 소요됩니다.

```bash
python train_model.py 
```

**5. 웹 애플리케이션 실행**
```bash
python app.py
```
* 서버가 실행되면, 웹 브라우저를 열고 주소창에 `http://127.0.0.1:5000` 을 입력하세요.

<br>

## 📊 모델 성능 (Model Performance)

'감성대화 말뭉치' 검증 데이터셋(Validation Set)으로 평가한 최종 모델의 성능은 다음과 같습니다.

| 평가지표 (Metric) | 점수 (Score) |
| :--- | :---: |
| **Accuracy** (정확도) | **85.3%** |
| **F1-Score** (Weighted)| **0.852** |


