# Emotion Diary 🤖

**하루를 마무리하며 쓰는 당신의 일기, 그 속에 숨겨진 진짜 감정은 무엇일까요?**

이 프로젝트는 AI를 통해 당신의 글을 이해하고, 감정에 몰입하거나 혹은 새로운 활력이 필요할 때 맞춤형 콘텐츠를 추천해주는 당신만의 감성 비서입니다.

---

### ✨ Live Demo

👉 **[https://huggingface.co/spaces/taehoon222/emotion-chatbot-app](https://huggingface.co/spaces/taehoon222/emotion-chatbot-app)**

---

### 📸 Screenshots

*(스크린샷을 여기에 추가하세요. 예: 메인 페이지, 일기 작성, 결과 화면)*

![Main Page](https://via.placeholder.com/400x250.png?text=Main+Page)
![Result Page](https://via.placeholder.com/400x250.png?text=Result+Page)

---

## 🚀 핵심 기능

- **🤖 텍스트 속 감정 탐색**: `klue/roberta-base` 모델을 기반으로, 일기 속에 담긴 복합적인 감정을 80% 이상의 정확도로 분석합니다.
- **🎭 감성 맞춤 큐레이션**: 분석된 감정에 따라 '수용'과 '전환' 두 가지 시나리오에 맞춰 영화, 음악, 책을 추천합니다.
- **📔 나만의 감정 기록**: 작성했던 일기와 AI의 감정 분석 결과를 달력 형태로 확인하고, 과거의 감정 흐름을 언제든지 다시 돌아볼 수 있습니다.
- **🎨 커스텀 테마**: 다양한 색상과 배경 이미지로 앱의 분위기를 취향에 맞게 변경할 수 있습니다.
- **💻 직관적인 반응형 UI**: Flask와 JavaScript로 구축된 간결하고 사용하기 쉬운 인터페이스를 제공합니다.

---

## 🛠️ 기술 스택

| 구분 | 기술 |
| :--- | :--- |
| **Backend** | Python, Flask, Gunicorn, SQLAlchemy |
| **Frontend**| HTML, CSS, JavaScript |
| **AI / Data**| PyTorch, Hugging Face Transformers, Scikit-learn, Pandas |
| **Database**| Supabase (PostgreSQL) |
| **Deployment**| Docker, GitHub Actions (CI/CD), Hugging Face Spaces |
| **Version Control**| Git, GitHub, Git LFS |

---

## 🏛️ 아키텍처

가벼운 앱 코드와 무거운 AI 모델을 분리하여 효율적인 CI/CD 파이프라인을 구축했습니다.

```
[Local PC] --(git push)--> [GitHub] --(Action)--> [Hugging Face Spaces]
                                                          |
                                                          | (App Start)
                                                          V
                                                 [Hugging Face Hub] <--(Download Model)-- [Spaces Server]
```

---

## 🏁 시작하기

### 사전 요구사항

- Python 3.10
- Anaconda (권장)

### 설치 및 실행

1.  **프로젝트 복제**
    ```bash
    git clone https://github.com/kootaeng2/Emotion-Chatbot-App.git
    cd Emotion-Chatbot-App
    ```

2.  **가상환경 생성 및 활성화 (Anaconda 사용)**
    ```bash
    conda create -n emotion_env python=3.10
    conda activate emotion_env
    ```

3.  **필수 라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정**
    `.env` 파일을 생성하고 아래 내용을 추가하세요. Gemini API를 통한 추천 기능에 필요합니다.
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

5.  **웹 애플리케이션 실행**
    ```bash
    python run.py
    ```

6.  **서버 접속**
    웹 브라우저에서 `http://127.0.0.1:5000` 주소로 접속하세요.

---

## 📂 프로젝트 구조

```
Emotion/
│
├── .github/            # GitHub Actions 워크플로우 (CI/CD)
├── data/               # AI 모델 학습용 데이터
├── notebooks/          # 데이터 탐색 및 전처리용 Jupyter Notebook
├── results/            # 모델 학습 결과
├── scripts/            # 모델 훈련, 평가용 스크립트
├── src/                # 핵심 애플리케이션 소스 코드
│   ├── templates/      # HTML 템플릿
│   ├── static/         # CSS, JS 파일
│   ├── __init__.py     # Flask 앱 초기화 (Application Factory)
│   ├── auth.py         # 인증 관련 로직
│   ├── emotion_engine.py # 감정 분석 모델 로딩 및 예측
│   ├── main.py         # 메인 페이지, 일기/추천 기능
│   └── models.py       # 데이터베이스 모델
│
├── supabase/           # Supabase DB 마이그레이션
├── Dockerfile          # 배포용 Docker 컨테이너 설정
├── requirements.txt    # Python 라이브러리 종속성
└── run.py              # 애플리케이션 실행 스크립트
```
<details>
<summary><strong>Frontend (Templates) 구조 상세 (클릭하여 펼치기)</strong></summary>

`src/templates` 폴더는 Flask의 Jinja2 템플릿 엔진을 사용하여 UI를 구성합니다. 역할에 따라 파일이 명확하게 분리되어 있으며, 상속과 매크로를 통해 효율적으로 UI를 관리합니다.

- **기본 레이아웃 (`base.html`, `base_auth.html`)**: 전체 페이지의 공통적인 뼈대(네비게이션 바 등)를 제공합니다.
- **개별 페이지 (`main.html`, `diary.html`, `page.html`, `login.html`, `signup.html`)**: 각 기능에 맞는 실제 페이지 UI를 담당하며, 기본 레이아웃을 상속받아 사용합니다.
- **재사용 컴포넌트 (`_macros.html`)**: 로그인 폼, 추천 탭 등 반복적으로 사용되는 UI 조각을 매크로 형태로 정의하여 코드 중복을 줄입니다.
- **정적 파일 (`static/`)**:
  - **`css/`**: 각 페이지에 특화된 스타일시트와 전역 스타일을 포함합니다.
  - **`js/`**: 페이지별 핵심 로직(API 통신, 달력 기능), 테마 변경, 온보딩 등 동적인 기능을 담당하는 JavaScript 파일들을 포함합니다.

</details>

---

## 🧗‍♂️ 개발 과정 및 문제 해결

프로젝트를 진행하며 겪었던 주요 기술적 도전과 해결 과정에 대한 자세한 내용은 **[DEVELOPMENT.md](DEVELOPMENT.md)** 파일에서 확인하실 수 있습니다.

---

## 📊 모델 성능

| Metric   | Score  |
| :------- | :----- |
| Accuracy | 0.7905 |
| F1 Score | 0.7910 |
| Loss     | 0.6943 |

---

## 📜 라이선스

This project is licensed under the MIT License.