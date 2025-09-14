---
language: ko
tags:
- text-classification
- emotion
- korean
license: mit
datasets:
- custom
model-name: korean-emotion-classifier
---

# Korean Emotion Classifier 😃😡😢😨😲😌

본 모델은 한국어 텍스트를 **6가지 감정(분노, 불안, 슬픔, 평온, 당황, 기쁨)**으로 분류합니다.
`klue/roberta-base` 기반으로 파인튜닝되었습니다.

---

## 📊 Evaluation Results

| Emotion | Precision | Recall | F1-Score |
|---------|-----------|--------|----------|
| 분노    | 0.9801    | 0.9788 | 0.9795   |
| 불안    | 0.9864    | 0.9848 | 0.9856   |
| 슬픔    | 0.9837    | 0.9854 | 0.9845   |
| 평온    | 0.9782    | 0.9750 | 0.9766   |
| 당황    | 0.9607    | 0.9668 | 0.9652   |
| 기쁨    | 0.9857    | 0.9886 | 0.9872   |

**Accuracy**: 0.9831
**Macro Avg**: Precision=0.9791 / Recall=0.9804 / F1=0.9798
**Weighted Avg**: Precision=0.9831 / Recall=0.9831 / F1=0.9831

```python
from transformers import pipeline
import torch

model_id = "Seonghaa/korean-emotion-classifier-roberta"

device = 0 if torch.cuda.is_available() else -1  # GPU 있으면 0, 없으면 CPU(-1)

clf = pipeline(
    "text-classification",
    model=model_id,
    tokenizer=model_id,
    device=device
)

texts = [
    "오늘 길에서 10만원을 주웠어",
    "오늘 친구들이랑 노래방에 갔어",
    "오늘 시험 망쳤어",
]

for t in texts:
    pred = clf(t, truncation=True, max_length=256)[0]
    print(f"입력: {t}")
    print(f"→ 예측 감정: {pred['label']}, 점수: {pred['score']:.4f}
")

```
## 출력 예시:
입력: 오늘 길에서 10만원을 주웠어</br>
→ 예측 감정: 기쁨, 점수: 0.9619

입력: 오늘 친구들이랑 노래방에 갔어</br>
→ 예측 감정: 기쁨, 점수: 0.9653

입력: 오늘 시험 망쳤어</br>
→ 예측 감정: 슬픔, 점수: 0.9602
