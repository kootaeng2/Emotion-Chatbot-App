# train_model.py
# AI 모델을 훈련하는 스크립트, 다시 사용가능한 삭제 x

import pandas as pd
import json
import re
import sys
import transformers
import torch

from transformers import AutoModelForSequenceClassification, AutoTokenizer

# --- 1. 데이터 로딩 및 전처리 ---

print("--- [Phase 1] 데이터 로딩 및 전처리 시작 ---")
# 파일 경로 설정
file_path = 'E:/sentiment_analysis_project/data/'

# 훈련/검증 데이터 로딩 (이전과 동일)
with open(file_path + 'training-label.json', 'r', encoding='utf-8') as file:
    training_data_raw = json.load(file)
with open(file_path + 'validation-label.json', 'r', encoding='utf-8') as file:
    validation_data_raw = json.load(file)

# DataFrame 생성 함수 (코드를 깔끔하게 하기 위해 함수로 묶음)
def create_dataframe(data_raw):
    extracted_data = []
    for dialogue in data_raw:
        try:
            emotion_type = dialogue['profile']['emotion']['type']
            dialogue_content = dialogue['talk']['content']
            full_text = " ".join(list(dialogue_content.values()))
            if full_text and emotion_type:
                extracted_data.append({'text': full_text, 'emotion': emotion_type})
        except KeyError:
            continue
    return pd.DataFrame(extracted_data)

df_train = create_dataframe(training_data_raw)
df_val = create_dataframe(validation_data_raw)

# 텍스트 정제
def clean_text(text):
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

df_train['cleaned_text'] = df_train['text'].apply(clean_text)
df_val['cleaned_text'] = df_val['text'].apply(clean_text)
print("✅ 데이터 로딩 및 전처리 완료!")


# --- 2. AI 모델링 준비 ---
print("\n--- [Phase 2] AI 모델링 준비 시작 ---")
# 모델 및 토크나이저 불러오기
MODEL_NAME = "beomi/kcbert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# 텍스트 토큰화
train_tokenized = tokenizer(list(df_train['cleaned_text']), return_tensors="pt", max_length=128, padding=True, truncation=True)
val_tokenized = tokenizer(list(df_val['cleaned_text']), return_tensors="pt", max_length=128, padding=True, truncation=True)

# 라벨 인코딩
unique_labels = sorted(df_train['emotion'].unique())
label_to_id = {label: id for id, label in enumerate(unique_labels)}
id_to_label = {id: label for label, id in label_to_id.items()}
df_train['label'] = df_train['emotion'].map(label_to_id)
df_val['label'] = df_val['emotion'].map(label_to_id)
print("✅ 토큰화 및 라벨 인코딩 완료!")
print("이제 모델 훈련을 위한 모든 준비가 끝났습니다.")


# [Phase 3]의 기존 코드를 아래 내용으로 교체해주세요.
# -----------------------------------------------------------
# --- [Phase 3] 모델 학습 및 평가 (최소 기능 버전) ---
# -----------------------------------------------------------
import torch
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

print("\n--- [Phase 3] 모델 학습 및 평가 시작 ---")

# 1. PyTorch Dataset 클래스 정의 (이전과 동일)
class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = EmotionDataset(train_tokenized, df_train['label'].tolist())
val_dataset = EmotionDataset(val_tokenized, df_val['label'].tolist())
print("✅ PyTorch 데이터셋 생성이 완료되었습니다.")

# 2. AI 모델 불러오기 (이전과 동일)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=len(unique_labels),
    id2label=id_to_label,
    label2id=label_to_id
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"✅ 모델 로딩 완료! 모델은 {device}에서 실행됩니다.")


# 3. 모델 성능 평가를 위한 함수 정의 (수정 완료)
def compute_metrics(pred):
    labels = pred.label_ids
    # 바로 이 부분이 수정되었습니다.
    preds = pred.predictions.argmax(-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

# 4. 훈련을 위한 상세 설정(Arguments) 정의 (모든 부가 옵션 제거)
training_args = TrainingArguments(
    output_dir='./results',          # 모델이 저장될 위치 (필수)
    num_train_epochs=3,              # 훈련 횟수
    per_device_train_batch_size=16,  # 훈련 배치 사이즈
    # 나머지 모든 평가/저장 관련 옵션은 모두 제거합니다.
)

# ---!!! 핵심 수정 사항 2 !!!---
# 5. Trainer 정의 (평가 관련 기능 비활성화)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    # 훈련 중 평가를 하지 않으므로 아래 옵션들은 제외합니다.
    # eval_dataset=val_dataset,
    # compute_metrics=compute_metrics
)

# 6. 모델 훈련 시작!
print("\n🔥 AI 모델 훈련을 시작합니다...")
trainer.train()
print("\n🎉 모델 훈련 완료!")

# 7. 최종 모델 평가는 훈련이 끝난 후 '별도로' 실행
print("\n--- 최종 모델 성능 평가 ---")
# 비활성화했던 평가 데이터셋을 evaluate 함수에 직접 전달해줍니다.
final_evaluation = trainer.evaluate(eval_dataset=val_dataset) 
print(final_evaluation)

print("\n모든 과정이 성공적으로 끝났습니다! results 폴더에서 훈련된 모델을 확인하세요.")