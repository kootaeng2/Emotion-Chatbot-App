```mermaid
graph LR

```
    %% 1. 클라이언트 영역
    subgraph Client ["💻 Client Side (Frontend)"]
        User[👤 사용자 / 웹 브라우저<br/>(HTML5, CSS3, JS)]
    end

    %% 2. 서버 영역
    subgraph Server ["⚙️ Flask Server (Backend)"]
        direction TB
        Controller[🎮 Main Controller<br/>(Routing & Logic)]
        InternalModel[🤖 Internal AI Engine<br/>(klue/roberta-base)]
    end

    %% 3. 인프라 및 외부 서비스 영역
    subgraph External ["☁️ Infrastructure & External APIs"]
        direction TB
        Gemini[✨ Google Gemini API<br/>(Generative AI Recommendation)]
        Supabase[(🗄️ Supabase DB<br/>PostgreSQL)]
    end

    %% --- 데이터 흐름 (Flow) ---
    
    %% 분석 단계
    User -- "1. 일기 작성 & 분석 요청 (/api/predict)" --> Controller
    Controller -- "2. 텍스트 전처리 & 추론" --> InternalModel
    InternalModel -- "3. 감정 라벨 & 확률 반환" --> Controller
    Controller -- "4. 추천 요청 (Prompting)" --> Gemini
    Gemini -- "5. 맞춤형 콘텐츠 생성" --> Controller
    Controller -- "6. 분석 결과(JSON) 응답" --> User

    %% 저장 단계
    User -- "7. '저장하기' 클릭 (/diary/save)" --> Controller
    Controller -- "8. 영구 저장 (INSERT)" --> Supabase

    %% 스타일링 (선택 사항)
    style Client fill:#e1f5fe,stroke:#01579b
    ```    
    style Server fill:#fff3e0,stroke:#e65100
    style External fill:#f3e5f5,stroke:#4a148c
    style InternalModel fill:#ffccbc,stroke:#bf360c,stroke-width:2px 
    ```
```
