
import os
import json
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer
from collections import Counter
import re

# --- [1] 설정 영역 ---
MODEL_PATH = "E:\\Emotion\\results\\checkpoint-32270"
TOKENIZER_PATH = "E:\\Emotion\\results\\nsmc_model"
TRAINING_FILE = "E:\\Emotion\\data\\training-label.json"
VALIDATION_FILE = "E:\\Emotion\\data\\validation-label.json"

# --- [2] train_upgrade.py와 동일한 데이터셋 클래스 및 전처리 함수 ---
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

def load_json_to_df(file_path: str) -> pd.DataFrame:
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    data_list = [
        {'text': " ".join(dialogue['talk']['content'].values()), 'emotion': dialogue['profile']['emotion']['type']}
        for dialogue in raw_data
        if dialogue.get('talk', {}).get('content') and dialogue.get('profile', {}).get('emotion', {}).get('type')
    ]
    return pd.DataFrame(data_list)

def clean_text(text: str) -> str:
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

# --- [3] 스크립트 실행 ---
def main():
    print("--- 오류 분석 스크립트 시작 ---")
    
    # 1. 훈련 데이터로부터 라벨 맵핑(label_to_id, id_to_label) 생성
    print(f"[1/5] 훈련 데이터 로딩: {TRAINING_FILE}")
    df_train = load_json_to_df(TRAINING_FILE)
    unique_labels = sorted(df_train['emotion'].unique())
    label_to_id = {label: i for i, label in enumerate(unique_labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}
    print("라벨 맵핑 생성 완료.")

    # 2. 분석할 모델과 토크나이저 로딩
    print(f"[2/5] 모델 로딩: {MODEL_PATH}")
    print(f"     토크나이저 로딩: {TOKENIZER_PATH}")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    
    # 3. 검증(validation) 데이터 로딩 및 전처리
    print(f"[3/5] 검증 데이터 로딩 및 전처리: {VALIDATION_FILE}")
    df_val = load_json_to_df(VALIDATION_FILE)
    df_val['cleaned_text'] = df_val['text'].apply(clean_text)
    df_val['label'] = df_val['emotion'].map(label_to_id)
    
    val_encodings = tokenizer(list(df_val['cleaned_text']), max_length=128, padding=True, truncation=True, return_tensors="pt")
    val_dataset = EmotionDataset(val_encodings, df_val['label'].tolist())
    print("검증 데이터셋 준비 완료.")

    # 4. 모델 예측 실행
    print("[4/5] 모델 예측 실행...")
    trainer = Trainer(model=model)
    predictions = trainer.predict(val_dataset)
    y_pred = np.argmax(predictions.predictions, axis=-1)
    y_true = predictions.label_ids
    print("예측 완료.")

    # 5. 오류 분석
    print("[5/5] 오류 분석 및 결과 출력...")
    errors = Counter()
    for true_label_id, pred_label_id in zip(y_true, y_pred):
        if true_label_id != pred_label_id:
            true_emotion = id_to_label[true_label_id]
            pred_emotion = id_to_label[pred_label_id]
            errors[(true_emotion, pred_emotion)] += 1
            
    print("\n--- 모델이 가장 많이 혼동하는 감정 쌍 (Top 15) ---")
    if not errors:
        print("축하합니다! 모델이 검증 데이터셋에서 단 하나의 오류도 만들지 않았습니다.")
    else:
        for (true_label, pred_label), count in errors.most_common(15):
            print(f"- 실제: {true_label} -> 예측: {pred_label} ({count}회)")
    print("--- 분석 완료 ---")

if __name__ == "__main__":
    main()
